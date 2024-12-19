import os, re, json, openai, time, math


def llm_error_handler(query_llm):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        while True:
            try:
                result = query_llm(*args, **kwargs)
                return result

            except openai.RateLimitError as exception:
                if "Retry-After" in exception.http_status:
                    retry_after = int(exception.headers.get("Retry-After", 60))
                else:
                    error_message = str(exception)
                    match = re.search(
                        r"Please retry after ([0-9]+) seconds", error_message
                    )
                    if not match:
                        print(f"Limit error: {exception}")
                        break
                    retry_after = int(match.group(1), 60)

                elapsed_time = (time.time() - start_time) // 60
                if elapsed_time >= 10:
                    print(f"Gave up retrying after {elapsed_time} minutes")
                    break

                print(f"Rate limit reached. Wait {retry_after} sec...")
                time.sleep(retry_after)

        return None

    return wrapper


@llm_error_handler
def query_llm_completion(llm_client, messages):
    completions = llm_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, max_tokens=600
    )
    return completions.choices[0].message.content


@llm_error_handler
def query_llm_embedding(llm_client, input_data):
    embeddings = llm_client.embeddings.create(
        input=[input_data], model="text-embedding-3-large"
    )
    return embeddings.data[0].embedding


def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be of the same length")

    def magnitude(vec):
        return math.sqrt(sum(a**2 for a in vec))

    magnitude_vec1 = magnitude(vec1)
    magnitude_vec2 = magnitude(vec2)
    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    return dot_product / (magnitude_vec1 * magnitude_vec2)


def process_similar_situations(llm_client, problem, situations_data):
    print(f"Problem: {problem}")
    problem_embedding = query_llm_embedding(llm_client, problem)

    situations_to_be_sorted = []
    for situation in situations_data.keys():
        situation_embedding = query_llm_embedding(llm_client, situation)
        situations_to_be_sorted.append(
            (situation, cosine_similarity(situation_embedding, problem_embedding))
        )

    situations_sorted = sorted(
        situations_to_be_sorted, key=lambda x: x[1], reverse=True
    )

    for situation in situations_sorted[:3]:
        print(f"Situation: ({situation[1]}) {situation[0]}")
        for advice in situations_data[situation[0]]:
            print(f" Advice: {advice}")
    return


def main():
    start_time = time.time()

    # High level config
    llm_client = openai.AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-07-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    with open("data/advices.md", "r") as f:
        text = f.read()

    section_pattern = re.compile(
        r"## (\d+\.\s[^\n]+)\n((?:\n|.)*?)(?=\n## |\Z)", re.MULTILINE
    )
    sections = section_pattern.findall(text)

    consolidated_data = {}
    for title, content in sections:

        while content and (content[-1] == "\n" or content[-1] == "-"):
            content = content[:-1]

        messages = [
            {
                "role": "system",
                "content": (
                    "Extract unique and relevant advices from the provided Markdown text. "
                    "For each piece of advice, generate a short description of the situation "
                    "where this advice is particularly valuable. Output JSON like this\n"
                    '[{"Situation": "situation",\n'
                    '"Advice": "advice"},]\n'
                    "Ensure output is pure JSON, no extra text."
                ),
            },
            {
                "role": "user",
                "content": f"Title: {title.strip()}\n\nText:\n{content}",
            },
        ]

        llm_output = query_llm_completion(llm_client, messages)

        llm_output_strip = llm_output.strip("`{}json \r\n\t\f")
        llm_output_json = json.loads(llm_output_strip)

        for item in llm_output_json:
            advice = item["Advice"]
            situation = item["Situation"]
            consolidated_data.setdefault(situation, set()).add(advice)

    process_similar_situations(
        llm_client,
        "I tried asking LLM for an explanation why water is blue for my preteen brother, but the brother was unable to understand LLM's answer "
        "using advanced physics. What practices related to LLMs will help?",
        consolidated_data,
    )

    process_similar_situations(
        llm_client,
        "When I ask LLM for structured data it always answers with JSon or Markdown and I need XML. How do I solve it?",
        consolidated_data,
    )

    print(time.time() - start_time)


main()
