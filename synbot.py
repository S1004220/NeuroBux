import re
import requests
import yfinance as yf
import streamlit as st
from cohere import ClientV2  # Optional: remove if not using Cohere

class SynBot:
    def __init__(self, provider="openrouter", model=None):
        """
        provider: "openrouter" or "cohere"
        model: defaults to:
            - OpenRouter: google/gemma-3n-e2b-it:free
            - Cohere: command-a-03-2025
        """
        self.provider = provider.lower()
        self.model = model or (
            "google/gemma-3n-e2b-it:free" if self.provider == "openrouter" else "command-a-03-2025"
        )

        if self.provider == "openrouter":
            self.api_key = st.secrets.get("openrouter_api_key")
            self.base_url = "https://openrouter.ai/api/v1"
        elif self.provider == "cohere":
            self.api_key = st.secrets.get("cohere_api_key")
        else:
            raise ValueError("Unsupported provider. Use 'openrouter' or 'cohere'.")

    def _format_financial_summary(self, df_exp, df_inc, analytics_data):
        parts = []

        if df_exp is not None and not df_exp.empty:
            spent = df_exp["Amount"].sum()
            parts.append(f"Total spent ₹{spent:.2f} across {len(df_exp)} transactions.")
            try:
                top_cat = df_exp.groupby("Category")["Amount"].sum().idxmax()
                avg_exp = df_exp["Amount"].mean()
                cat_split = df_exp.groupby("Category")["Amount"].sum().to_dict()
                parts += [
                    f"Top category: {top_cat}",
                    f"Average expense: ₹{avg_exp:.2f}",
                    f"Category breakdown: {cat_split}"
                ]
            except Exception:
                pass

        if df_inc is not None and not df_inc.empty:
            earned = df_inc["Amount"].sum()
            avg_inc = df_inc["Amount"].mean()
            parts += [
                f"Total income: ₹{earned:.2f} from {len(df_inc)} sources.",
                f"Average income: ₹{avg_inc:.2f}"
            ]
            if df_exp is not None and not df_exp.empty:
                parts.append(f"Net balance: ₹{earned - df_exp['Amount'].sum():.2f}")

        if analytics_data:
            trend = analytics_data.get("trend", 1)
            trend_status = "increasing" if trend > 1.1 else "stable" if trend > 0.9 else "decreasing"
            parts.append(
                f"Spending patterns: peak on {analytics_data.get('peak_day', 'weekdays')}, "
                f"trend: {trend_status}, top category: {analytics_data.get('top_category', 'miscellaneous')}."
            )

        return " ".join(parts)

    def _live_price(self, symbol):
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period="1d", interval="1m")
            if df.empty:
                return f"❌ *{symbol.upper()}*: no recent trades."
            last = df.iloc[-1]
            chg = (last.Close - last.Open) / last.Open * 100
            return f"📈 *{symbol.upper()}*\nPrice: **${last.Close:.2f}**\nChange: **{chg:+.2f}%**"
        except Exception as e:
            return f"⚠ *{symbol}*: {e}"

    def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):
        q_clean = question.strip()
        symbol_match = re.search(r"\b([A-Z]{2,5})\b", q_clean.upper())
        if "price" in q_clean.lower() and symbol_match:
            return self._live_price(symbol_match.group(1))

        context = self._format_financial_summary(df_exp, df_inc, analytics_data)
        if not self.api_key:
            return f"🤖 API Key missing! Please add your {self.provider.title()} API key to Streamlit secrets."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are SynBot, a knowledgeable financial AI assistant for NeuroBux. "
                    "Analyze spending patterns, give budgeting & saving tips, investment basics, and motivational advice. "
                    "Be friendly, concise, and occasionally use emojis."
                )
            },
            {
                "role": "user",
                "content": f"Question: {q_clean}\n\nUser's Financial Context: {context}"
            }
        ]

        if self.provider == "openrouter":
            return self._call_openrouter_api(messages)
        elif self.provider == "cohere":
            return self._call_cohere_stream(messages)

    def _call_openrouter_api(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurobux.streamlit.app/",
            "X-Title": "NeuroBux Finance Tracker"
        }
        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=30
            )
            error_messages = {
                401: "🔑 Authentication Failed! Check your API key.",
                429: "⏳ Rate Limit Exceeded! Try again later.",
                403: "🚫 Access Forbidden! Model permission issue."
            }
            if r.status_code in error_messages:
                return error_messages[r.status_code]
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            return "⏰ Request Timeout! Please try again."
        except requests.exceptions.ConnectionError:
            return "🌐 Connection Error! Check internet."
        except requests.exceptions.HTTPError as e:
            return f"🤖 API Error! HTTP {r.status_code}: {r.text[:100]}..."
        except (KeyError, IndexError):
            return "🤖 Invalid Response Format!"
        except Exception as e:
            return f"🤖 Unexpected Error: {str(e)[:100]}..."

    def _call_cohere_stream(self, messages):
        try:
            client = ClientV2(api_key=self.api_key)
            cohere_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
            stream = client.chat_stream(model=self.model, messages=cohere_messages, temperature=0.3)
            output = []
            for event in stream:
                if event.type == "content-delta":
                    output.append(event.delta.message.content.text)
            return "".join(output).strip()
        except Exception as e:
            return f"🤖 Cohere Error: {str(e)[:100]}"

class SmartBudgetAdvisor:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer

    def generate_budget_insights(self, user_data, patterns):
        insights = []

        trend = patterns.get('spending_trend', 1)
        if trend > 1.2:
            insights.append({
                'type': 'warning',
                'message': f"📈 Spending increased by {(trend - 1) * 100:.1f}%",
                'suggestion': "Review purchases, set daily limits, and try the 24-hour rule for non-essentials over ₹500."
            })
        elif trend < 0.8:
            insights.append({
                'type': 'positive',
                'message': f"📉 Spending decreased by {(1 - trend) * 100:.1f}%",
                'suggestion': "Great job! Allocate savings into an emergency fund or investments."
            })

        top_cat = patterns.get('top_category', 'N/A')
        if top_cat != 'N/A':
            insights.append({
                'type': 'insight',
                'message': f"💡 Highest spending category: {top_cat}",
                'suggestion': f"Use envelope budgeting for {top_cat}, set monthly limits, and review weekly."
            })

        unusual = patterns.get('unusual_expenses', [])
        if unusual:
            count = len(unusual)
            insights.append({
                'type': 'alert',
                'message': f"⚠ {count} unusual expense{'s' if count > 1 else ''} detected",
                'suggestion': "Review these transactions; decide if one-time or require budget adjustments."
            })

        return insights
