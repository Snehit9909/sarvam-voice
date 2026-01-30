from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="sk_pan06xjq_quAeCvDv57KZWsIyXsXuDc2t",
)

response = client.text.translate(
    input="Hi, My Name is Vinayak.",
    source_language_code="auto",
    target_language_code="kn-IN",
    speaker_gender="Male"
)

print(response)
