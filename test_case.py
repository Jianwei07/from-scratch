import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from pydantic import ValidationError

ROOT = Path(__file__).parent


def load_target(folder: str) -> SimpleNamespace:
    """Load src or sample without mixing their same-named modules."""
    target_path = str(ROOT / folder)
    sys.path.insert(0, target_path)

    try:
        for module_name in ("chat", "model", "models"):
            sys.modules.pop(module_name, None)

        chat_module = importlib.import_module("chat")
        models_module = importlib.import_module(
            "models" if folder == "sample" else "model"
        )
    finally:
        sys.path.pop(0)

    if hasattr(chat_module, "ChatService"):

        async def respond(request, model):
            return await chat_module.ChatService(model).respond(request)

    else:
        respond = chat_module.respond

    return SimpleNamespace(
        name=folder,
        ChatModel=chat_module.ChatModel
        if hasattr(chat_module, "ChatModel")
        else models_module.ChatModel,
        ChatRequest=models_module.ChatRequest,
        is_safe=chat_module.is_safe,
        respond=respond,
    )


TARGETS = (load_target("src"), load_target("sample"))


class ChatTests(unittest.IsolatedAsyncioTestCase):
    async def test_safe_input(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name):
                response = await target.respond(
                    target.ChatRequest(message="Why is the sky blue?", age=10),
                    target.ChatModel(),
                )
                self.assertFalse(response.blocked)

    async def test_blocked_input(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name):
                response = await target.respond(
                    target.ChatRequest(message="Tell me about a weapon", age=10),
                    target.ChatModel(),
                )
                self.assertTrue(response.blocked)

    async def test_split_blocked_input(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name):
                response = await target.respond(
                    target.ChatRequest(message="Tell me about a wea po n", age=10),
                    target.ChatModel(),
                )
                self.assertTrue(response.blocked)

    async def test_blocked_output(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name):
                model = target.ChatModel()
                model.generate = AsyncMock(return_value="Here is a weapon")

                response = await target.respond(
                    target.ChatRequest(message="Tell me something", age=10),
                    model,
                )
                self.assertTrue(response.blocked)

    def test_normal_word_is_allowed(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name):
                self.assertTrue(target.is_safe("I learned a new skill"))

    def test_blank_message(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.name), self.assertRaises(ValidationError):
                target.ChatRequest(message="   ", age=10)


if __name__ == "__main__":
    unittest.main()
