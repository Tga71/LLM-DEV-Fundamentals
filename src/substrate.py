import os, re, json, openai, time


def query_llm(llm_client, messages):
    start_time = time.time()

    while True:
        try:
            # Get Response
            completion = llm_client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=600
            )
            return completion.choices[0].message.content

        except openai.RateLimitError as e:
            if "Retry-After" not in e.http_status:
                print(f"Limit error: {e}")
                break

            elapsed_time = (time.time() - start_time) // 60
            if elapsed_time >= 10:
                print(f"Gave up retrying after {elapsed_time} minutes")
                break

            retry_after = int(e.headers.get("Retry-After", 60))
            print(f"Rate limit reached. Wait {retry_after} sec...")
            time.sleep(retry_after)

    return None


def test_query_llm(*ignore):
    return """[{"Situation": "When you need to guide AI to deliver focused and clear responses in a complex topic.",
"Advice": "Use the Scaffolding Pattern by breaking down complex prompts into smaller, focused components."},
{"Situation": "When the AI response tends to be off-topic or vague.",
"Advice": "Apply the Redirection Pattern to refine prompts, ensuring AI is guided towards desired outcomes."},
{"Situation": "For inquiries that require a natural conversation flow and follow-up questions.",
"Advice": "Implement the Multi-Step Pattern for dynamic exchanges, letting prompts build upon previous responses."},
{"Situation": "When you want to ensure AI-generated content aligns with specific requirements and ethical guidelines.",
"Advice": "Utilize the Constraint Pattern to set explicit boundaries in prompts."},
{"Situation": "When seeking creative, versatile, and engaging interactions with AI.",
"Advice": "Adopt the Act As Pattern to instruct AI to take on alternate personas or roles."},
{"Situation": "When you have structured data and need insights or visual representations from the AI.",
"Advice": "Utilize the Data Pattern to analyze structured data like JSON or CSV for insights."},
{"Situation": "When dealing with unsatisfactory responses from AI and needing to adapt your approach.",
"Advice": "Use the Fallback Pattern to manage and improve upon disappointing AI outputs."},
{"Situation": "When seeking accurate AI responses but facing clarification issues.",
"Advice": "Focus on Handling Ambiguous Prompts by enhancing specificity and clarity in your prompts."},
{"Situation": "Formatting chatbot outputs",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "Formatting chatbot outputs",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "Formatting chatbot outputs",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "When needing a thorough analysis of an issue.",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "Introducing specific structure in responses",
"Advice": "Provide Examples of how you want information structured, such as using the STAR framework."},
{"Situation": "When needing a thorough analysis of an issue.",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "Introducing specific structure in responses",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "When needing a thorough analysis of an issue.",
"Advice": "Specify the Format to visualize how you want the output to look, such as emails or paragraphs."},
{"Situation": "Determining the emotional tone of chatbot responses",
"Advice": "Define the Tone by selecting keywords that convey the desired emotional response, like casual or formal."}]"""


def main():

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
            {"role": "user", "content": f"Title: {title.strip()}\n\nText:\n{content}"},
        ]

        llm_output = query_llm(llm_client, messages)

        llm_output_strip = llm_output.strip().strip("`")
        if llm_output_strip.startswith("json"):
            llm_output_strip = llm_output_strip[4:]
        llm_output_json = json.loads(llm_output_strip)

        for item in llm_output_json:
            advice = item["Advice"]
            situation = item["Situation"]
            consolidated_data.setdefault(advice, set()).add(situation)

    for advice, situations in consolidated_data.items():
        for situation in situations:
            print(f"Situation: {situation}")
        print(f" Advice: {advice}")


main()
