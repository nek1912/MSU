
import re
from typing import Optional

import httpx

from app.config import REQUEST_TIMEOUT_S, get_settings


DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_TEMPERATURE = 0

DEFAULT_MAX_TOKENS = 1800

REPAIR_MAX_TOKENS = 2200

GENERATION_ATTEMPTS_PER_KEY = 2


CITATION_PATTERN = re.compile(
    r"\[EVIDENCE\s+(\d+)\]",
    re.IGNORECASE,
)

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class AnswerGenerator:

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        print("Initializing RAG answer generator...")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        settings = get_settings()
        self._api_key = settings.groq_api_key

        if not self._api_key:
            raise RuntimeError(
                "No Groq API key configured."
            )

        print(
            f"RAG answer generator ready.\n"
            f"Model         : {self.model}\n"
            f"Temperature    : {self.temperature}\n"
            f"Max tokens     : {self.max_tokens}"
        )


    def _call_groq(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float = 0,
        reasoning_effort: str | None = None,
    ) -> dict:
        """Make a single httpx POST call to the Groq API."""
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort

        r = httpx.post(
            _GROQ_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json=payload,
            timeout=REQUEST_TIMEOUT_S,
        )
        r.raise_for_status()
        return r.json()


    @staticmethod
    def _extract_message_content(
        data: dict,
    ) -> Optional[str]:
        """
        Safely extract visible answer text from a Groq/OpenAI
        compatible response dict.
        """

        choices = data.get("choices", [])
        if not choices:
            return None

        message = choices[0].get("message", {})
        if not message:
            return None

        content = message.get("content")

        if isinstance(content, str):
            content = content.strip()
            if content:
                return content

        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, str):
                    text = block.strip()
                    if text:
                        parts.append(text)
                elif isinstance(block, dict):
                    text = block.get("text")
                    if isinstance(text, str):
                        text = text.strip()
                        if text:
                            parts.append(text)
            if parts:
                return "\n".join(parts).strip()

        return None


    @staticmethod
    def _extract_evidence_numbers(
        user_prompt: str,
    ) -> set[int]:
        """
        Extract all evidence numbers available inside the
        grounded user prompt.
        """

        matches = CITATION_PATTERN.findall(
            user_prompt
        )

        return {
            int(number)
            for number in matches
        }


    @staticmethod
    def _extract_answer_citations(
        answer: str,
    ) -> set[int]:
        """
        Extract unique evidence numbers cited by the answer.
        """

        matches = CITATION_PATTERN.findall(
            answer
        )

        return {
            int(number)
            for number in matches
        }


    @staticmethod
    def _citation_count(
        answer: str,
    ) -> int:
        """
        Count every visible citation occurrence.
        """

        return len(
            CITATION_PATTERN.findall(
                answer
            )
        )


    @staticmethod
    def _clean_answer(
        answer: str,
    ) -> str:
        """
        Remove accidental model wrappers without changing
        the actual answer content.
        """

        if not answer:
            return ""

        answer = answer.strip()


        if (
            answer.startswith("```")
            and answer.endswith("```")
        ):
            lines = answer.splitlines()

            if len(lines) >= 2:
                first = lines[0].strip()

                if first.lower() in (
                    "```markdown",
                    "```md",
                    "```text",
                    "```",
                ):
                    answer = "\n".join(
                        lines[1:-1]
                    ).strip()

        return answer


    @staticmethod
    def _strip_citations(
        text: str,
    ) -> str:
        """
        Remove citations from a piece of text for semantic
        classification only.
        """

        return CITATION_PATTERN.sub(
            "",
            text,
        ).strip()


    @staticmethod
    def _is_heading(
        line: str,
    ) -> bool:
        """
        Determine whether a line is probably a markdown heading.
        """

        stripped = line.strip()

        if not stripped:
            return False

        if re.match(
            r"^#{1,6}\s+",
            stripped,
        ):
            return True

        without_markdown = re.sub(
            r"[*_`>#]",
            "",
            stripped,
        ).strip()

        if (
            len(without_markdown) < 80
            and not re.search(
                r"[.!?]\s*$",
                without_markdown,
            )
            and not re.search(
                r"\b(is|are|was|were|means|refers|provides|requires)\b",
                without_markdown,
                re.IGNORECASE,
            )
        ):
            return True

        return False


    @staticmethod
    def _is_bullet(
        line: str,
    ) -> bool:
        """
        Detect markdown bullet/list lines.
        """

        return bool(
            re.match(
                r"^\s*(?:[-*+]|\d+[.)])\s+",
                line,
            )
        )


    @staticmethod
    def _remove_markdown_prefix(
        line: str,
    ) -> str:
        """
        Remove markdown decoration for validation only.
        """

        line = re.sub(
            r"^\s*#{1,6}\s*",
            "",
            line,
        )

        line = re.sub(
            r"^\s*(?:[-*+]|\d+[.)])\s+",
            "",
            line,
        )

        return line.strip()


    @staticmethod
    def _has_substantive_text(
        text: str,
    ) -> bool:
        """
        Determine whether text contains enough actual prose to
        require grounding.
        """

        cleaned = AnswerGenerator._strip_citations(
            text
        )

        cleaned = re.sub(
            r"[*_`>#]",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        compact = re.sub(
            r"[\s:;,.!?()\[\]{}\-\u2013\u2014]+",
            "",
            cleaned,
        )

        return len(compact) >= 20


    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:
        """
        Lightweight sentence splitter.
        """

        text = text.strip()

        if not text:
            return []

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        parts = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9\"'\u201c\u2018(])",
            text,
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]


    def _citation_validation_details(
        self,
        answer: str,
        user_prompt: str,
        ) -> tuple[bool, list[str]]:
        """
        Validate citation usage.
        """

        reasons: list[str] = []


        valid_evidence_numbers = (
            self._extract_evidence_numbers(
                user_prompt
            )
        )

        if not valid_evidence_numbers:
            reasons.append(
                "No [EVIDENCE N] blocks were found in the grounded prompt."
            )

            return False, reasons


        answer_citations = (
            self._extract_answer_citations(
                answer
            )
        )

        if not answer_citations:
            reasons.append(
                "The answer contains no [EVIDENCE N] citation."
            )

            return False, reasons


        invalid_citations = (
            answer_citations
            - valid_evidence_numbers
        )

        if invalid_citations:
            reasons.append(
                "Answer cites nonexistent evidence numbers: "
                f"{sorted(invalid_citations)}"
            )

        if not invalid_citations:
            return True, []

        return False, reasons

        def flush_block():
            if current_block:
                block = "\n".join(
                    current_block
                ).strip()

                if block:
                    blocks.append(block)

                current_block.clear()

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                flush_block()
                continue

            if self._is_heading(line):
                flush_block()
                blocks.append(line)
                continue

            current_block.append(line)

        flush_block()


        factual_blocks: list[tuple[int, str]] = []

        for index, block in enumerate(blocks, start=1):

            if self._is_heading(block):
                continue

            if not self._has_substantive_text(block):
                continue

            factual_blocks.append(
                (index, block)
            )

        if not factual_blocks:
            reasons.append(
                "No substantive factual content was found in the answer."
            )

            return False, reasons


        uncited_blocks: list[int] = []

        for block_index, block in factual_blocks:

            if not CITATION_PATTERN.search(
                block
            ):
                uncited_blocks.append(
                    block_index
                )

        if uncited_blocks:
            reasons.append(
                "Substantive blocks without citations: "
                f"{uncited_blocks}"
            )


        is_valid = not reasons

        return is_valid, reasons


    def _citations_are_valid(
        self,
        answer: str,
        user_prompt: str,
    ) -> bool:
        """
        Validate answer citations.
        """

        valid, reasons = (
            self._citation_validation_details(
                answer=answer,
                user_prompt=user_prompt,
            )
        )

        if not valid:
            print(
                "Citation validation diagnostics:"
            )

            for reason in reasons:
                print(
                    f"  - {reason}"
                )

        return valid


    def _generate_with_client(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        data = self._call_groq(
            messages=messages,
            max_tokens=(
                max_tokens
                if max_tokens is not None
                else self.max_tokens
            ),
            temperature=self.temperature,
            reasoning_effort=reasoning_effort,
        )

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(
                "LLM returned no choices."
            )

        message = choices[0].get("message")
        if message is None:
            raise RuntimeError(
                "LLM returned an empty message."
            )

        answer = self._extract_message_content(data)

        if not answer:
            finish_reason = choices[0].get("finish_reason")
            reasoning = message.get("reasoning", "")
            reasoning_length = (
                len(reasoning)
                if isinstance(reasoning, str)
                else 0
            )

            raise RuntimeError(
                "LLM returned an empty visible answer. "
                f"finish_reason={finish_reason}, "
                f"reasoning_length={reasoning_length}"
            )

        answer = self._clean_answer(
            answer
        )

        if not answer:
            raise RuntimeError(
                "LLM returned a whitespace-only answer."
            )

        return answer


    def _repair_citations(
        self,
        system_prompt: str,
        user_prompt: str,
        draft_answer: str,
    ) -> str:
        """
        Repair citation coverage while preserving the original
        answer as much as possible.
        """

        repair_system_prompt = """
You are the citation repair layer of eGovAssist.

Your ONLY task is to add missing [EVIDENCE N] citations to the
supplied draft answer.

DO NOT rewrite the answer.

DO NOT summarize the answer.

DO NOT add facts.

DO NOT remove facts.

DO NOT change facts.

DO NOT change the meaning.

DO NOT change the order of the answer.

DO NOT create new paragraphs.

DO NOT merge paragraphs.

DO NOT create a Sources section.

Preserve the original wording and structure exactly whenever
possible.

You may ONLY insert citation markers.

Valid citation format:

[EVIDENCE 1]

or:

[EVIDENCE 1] [EVIDENCE 3]

IMPORTANT:

Use ONLY evidence numbers that actually occur in the ORIGINAL
GROUNDED REQUEST.

Citation rules:

1. Every substantive factual paragraph/block must contain at
   least one valid citation.

2. Every factual bullet must contain at least one valid citation.

3. Headings do not require citations.

4. If a paragraph contains several factual sentences that are
   supported by the same evidence, one citation at the end of
   that paragraph is sufficient.

5. Put citations at the end of the sentence or factual bullet
   they support.

6. Do not add citations merely to increase citation count.

7. Never invent an evidence number.

8. Never cite nonexistent evidence.

9. Do not explain the repair.

10. Return ONLY the repaired answer.

11. Keep the complete original answer.

12. Never intentionally truncate the answer.

13. Do not replace existing valid citations unless necessary.

IMPORTANT:
The output must contain visible answer text.
Do not return an empty response.
"""

        repair_user_prompt = (
            "ORIGINAL GROUNDED REQUEST:\n"
            f"{user_prompt}\n\n"
            "DRAFT ANSWER TO REPAIR:\n"
            f"{draft_answer}\n\n"
            "TASK:\n"
            "Insert only the missing valid [EVIDENCE N] citation "
            "markers into the draft answer. Preserve all original "
            "wording, facts, structure, paragraph order, and "
            "formatting. Do not add or remove information. "
            "Every substantive factual paragraph or factual bullet "
            "must have at least one valid citation. If an existing "
            "citation already covers a factual paragraph, leave it "
            "alone. Return ONLY the complete repaired answer."
        )


        data = self._call_groq(
            messages=[
                {
                    "role": "system",
                    "content": repair_system_prompt,
                },
                {
                    "role": "user",
                    "content": repair_user_prompt,
                },
            ],
            max_tokens=REPAIR_MAX_TOKENS,
            temperature=0,
            reasoning_effort="low",
        )

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(
                "Citation repair returned no choices."
            )

        message = choices[0].get("message")
        if message is None:
            raise RuntimeError(
                "Citation repair returned an empty message."
            )

        repaired_answer = (
            self._extract_message_content(data)
        )

        if not repaired_answer:
            finish_reason = choices[0].get("finish_reason")
            reasoning = message.get("reasoning", "")
            reasoning_length = (
                len(reasoning)
                if isinstance(reasoning, str)
                else 0
            )

            raise RuntimeError(
                "Citation repair returned an empty "
                "visible answer. "
                f"finish_reason={finish_reason}, "
                f"reasoning_length={reasoning_length}"
            )

        repaired_answer = self._clean_answer(
            repaired_answer
        )

        if not repaired_answer:
            raise RuntimeError(
                "Citation repair returned a "
                "whitespace-only answer."
            )

        if len(repaired_answer.strip()) < 20:
            raise RuntimeError(
                "Citation repair returned an unexpectedly "
                "short answer."
            )

        return repaired_answer


    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:

        system_prompt = system_prompt.strip()
        user_prompt = user_prompt.strip()

        if not system_prompt:
            raise ValueError(
                "System prompt cannot be empty."
            )

        if not user_prompt:
            raise ValueError(
                "User prompt cannot be empty."
            )


        available_evidence = (
            self._extract_evidence_numbers(
                user_prompt
            )
        )

        if not available_evidence:
            raise RuntimeError(
                "No [EVIDENCE N] blocks were found in "
                "the retrieved context."
            )

        print(
            "Available evidence numbers: "
            f"{sorted(available_evidence)}"
        )

        last_error = None

        for attempt in range(
            1,
            GENERATION_ATTEMPTS_PER_KEY + 1,
        ):

            print(
                f"Generation attempt "
                f"{attempt}/"
                f"{GENERATION_ATTEMPTS_PER_KEY}..."
            )

            try:

                answer = self._generate_with_client(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=self.max_tokens,
                    reasoning_effort="low",
                )

                citation_count = (
                    self._citation_count(
                        answer
                    )
                )

                print(
                    "Initial answer citation count: "
                    f"{citation_count}"
                )


                citations_valid = (
                    self._citations_are_valid(
                        answer=answer,
                        user_prompt=user_prompt,
                    )
                )

                if citations_valid:

                    print(
                        "Citation validation successful."
                    )

                else:

                    print(
                        "Citation validation failed."
                    )

                    print(
                        "Starting citation repair pass..."
                    )


                    try:

                        repaired_answer = (
                            self._repair_citations(
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                draft_answer=answer,
                            )
                        )

                    except Exception as repair_error:

                        print(
                            "Citation repair failed:"
                        )

                        print(
                            f"Reason: {repair_error}"
                        )

                        raise RuntimeError(
                            "Citation repair failed: "
                            f"{repair_error}"
                        )

                    repaired_citation_count = (
                        self._citation_count(
                            repaired_answer
                        )
                    )

                    print(
                        "Repaired answer citation count: "
                        f"{repaired_citation_count}"
                    )


                    repaired_citations = (
                        self._extract_answer_citations(
                            repaired_answer
                        )
                    )

                    invalid_repaired_citations = (
                        repaired_citations
                        - available_evidence
                    )

                    if invalid_repaired_citations:

                        raise RuntimeError(
                            "Citation repair introduced "
                            "invalid evidence numbers: "
                            f"{sorted(invalid_repaired_citations)}"
                        )


                    repaired_valid = (
                        self._citations_are_valid(
                            answer=repaired_answer,
                            user_prompt=user_prompt,
                        )
                    )

                    if not repaired_valid:

                        raise RuntimeError(
                            "Citation repair completed, "
                            "but the resulting answer "
                            "still failed citation "
                            "validation."
                        )

                    answer = repaired_answer

                    print(
                        "Citation repair successful."
                    )


                print(
                    f"RAG generation "
                    f"successful."
                )

                return {
                    "status": "success",
                    "answer": answer,
                    "provider": "groq",
                    "model": self.model,
                }

            except Exception as error:

                last_error = error

                print(
                    f"RAG generation attempt "
                    f"{attempt}/"
                    f"{GENERATION_ATTEMPTS_PER_KEY} "
                    f"failed."
                )

                print(
                    f"Reason: {error}"
                )

                if (
                    attempt
                    < GENERATION_ATTEMPTS_PER_KEY
                ):

                    print(
                        "Retrying generation..."
                    )


        # Groq exhausted — fallback to Gemini
        print("Groq exhausted, falling back to Gemini...")
        try:
            answer = self._generate_with_gemini(
                system_prompt, user_prompt
            )
            return answer
        except Exception as gemini_error:
            raise RuntimeError(
                "All configured LLM attempts failed "
                "during RAG answer generation. "
                f"Groq last error: {last_error}. "
                f"Gemini error: {gemini_error}"
            )

    def _generate_with_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Fallback to Gemini when Groq is rate-limited."""
        settings = get_settings()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash-lite:generateContent?key={settings.gemini_api_key}"
        )
        r = httpx.post(
            url,
            json={
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": DEFAULT_TEMPERATURE},
            },
            timeout=REQUEST_TIMEOUT_S,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]


_generator = None


def generate_answer(
    system_prompt: str,
    user_prompt: str,
) -> dict:

    global _generator

    if _generator is None:
        _generator = AnswerGenerator()

    return _generator.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
