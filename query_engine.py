import requests, json

class OllamaAdapter:
    def __init__(self, model="llama3.1", base_url="http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url

    def call_ollama(self, prompt: str):
        import requests, json

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        res = requests.post(f"{self.base_url}/api/generate", json=payload)
        res.raise_for_status()

        lines = res.text.strip().split("\n")

        full_text = ""
        for line in lines:
            try:
                data = json.loads(line)
                full_text += data.get("response", "")
            except:
                pass

        return full_text

