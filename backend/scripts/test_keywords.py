text = "regarding gujarat agriculture, my cotton crop has been spoiled. what should i do now?"
text_lower = text.lower()
rules = {
    "pmfby": ["pmfby", "crop insurance", "crop loss", "crop damage", "claim"],
    "agriculture": ["cotton", "crop failure", "what should i do", "harvest", "crop"],
}
for domain, keywords in rules.items():
    matches = [kw for kw in keywords if kw in text_lower]
    if matches:
        print(f"{domain}: {matches}")
