from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="sk_pan06xjq_quAeCvDv57KZWsIyXsXuDc2t",
)

response = client.text_to_speech.convert(
    text="Hello, how are you?",
    target_language_code="hi-IN",
)

print(response)
