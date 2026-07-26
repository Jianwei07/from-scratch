import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from pydantic import ValidationError

ROOT = Path(__file__).parent


def load_target(folder: str) -> SimpleNamespace:
    """Load a target without mixing its same-named modules."""
    target_path = str(ROOT / folder)
    sys.path.insert(0, target_path)

    try:
        for module_name in ("chat", "model", "models"):
            sys.modules.pop(module_name, None)

        chat_module = importlib.import_module("chat")
        models_module = importlib.import_module(
            "models" if folder.startswith("sample") else "model"
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
        ChatService=getattr(chat_module, "ChatService", None),
        ConversationStore=getattr(chat_module, "ConversationStore", None),
        ChatRequest=models_module.ChatRequest,
        is_safe=chat_module.is_safe,
        respond=respond,
    )


TARGETS = (load_target("src"), load_target("sample"))
HISTORY_TARGET = load_target("sample_wif_store")


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


class ConversationHistoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_conversation_can_continue_and_be_retrieved(self) -> None:
        target = HISTORY_TARGET
        service = target.ChatService(
            target.ChatModel(),
            target.ConversationStore(),
        )

        first = await service.respond(
            target.ChatRequest(message="Hello", age=10)
        )
        second = await service.respond(
            target.ChatRequest(
                message="Tell me more",
                age=10,
                conversation_id=first.conversation_id,
            )
        )
        history = service.get_history(first.conversation_id)

        self.assertEqual(second.conversation_id, first.conversation_id)
        self.assertEqual(
            [message.role for message in history.messages],
            ["user", "assistant", "user", "assistant"],
        )
        self.assertEqual(history.messages[0].content, "Hello")
        self.assertEqual(history.messages[2].content, "Tell me more")

    def test_unknown_conversation_is_rejected(self) -> None:
        target = HISTORY_TARGET
        service = target.ChatService(
            target.ChatModel(),
            target.ConversationStore(),
        )

        with self.assertRaises(KeyError):
            service.get_history("missing")


if __name__ == "__main__":
    unittest.main()
