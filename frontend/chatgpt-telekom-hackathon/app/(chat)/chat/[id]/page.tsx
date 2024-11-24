import { cookies } from 'next/headers';
import { notFound } from 'next/navigation';

import { Chat as PreviewChat } from '@/components/chat';
import { DEFAULT_MODEL_NAME, models } from '@/lib/ai/models';
import {Message} from "ai";

const fakeMessages: Message[] = [
  {
    id: 'b6e29c88-1d91-4b1d-9382-34c09b8d8f1d',
    role: 'user',
    content: 'Hello, how are you?',
    createdAt: new Date('2024-11-01T10:00:00Z'),
  },
  {
    id: 'f8cba10e-5a33-4ae8-a6f4-3d2be3bf60bd',
    role: 'assistant',
    content: 'I’m good, thank you! How can I assist you today?',
    createdAt: new Date('2024-11-01T10:01:00Z'),
  },
  {
    id: 'c37d8c16-772b-41e1-a343-e5d015be2747',
    role: 'user',
    content: 'Can you tell me about your features?',
    createdAt: new Date('2024-11-01T10:02:00Z'),
  },
  {
    id: '7fd23af4-5f65-4a76-a8e1-1b01dc7de421',
    role: 'assistant',
    content: 'Of course! I can help with chatting, providing information, and more.',
    createdAt: new Date('2024-11-01T10:03:00Z'),
  },
  {
    id: '913a6d90-8d3e-4d35-bd5c-dc45b31f0931',
    role: 'user',
    content: 'What kind of information can you provide?',
    createdAt: new Date('2024-11-01T10:04:00Z'),
  },
  {
    id: '3e88a071-0d21-432d-b82f-5a713b78d4e8',
    role: 'assistant',
    content: 'I can provide information on various topics, from programming to general knowledge.',
    createdAt: new Date('2024-11-01T10:05:00Z'),
  },
  {
    id: 'b6c29ef8-1d23-4b4d-a234-34c18f3b81df',
    role: 'user',
    content: 'Can you help me with some JavaScript questions?',
    createdAt: new Date('2024-11-01T10:06:00Z'),
  },
  {
    id: 'f3e7ac20-2a9f-4ebf-94e6-6c3b2e41e2db',
    role: 'assistant',
    content: 'Absolutely! Feel free to ask any JavaScript-related question.',
    createdAt: new Date('2024-11-01T10:07:00Z'),
  },
  {
    id: '2d8b6a81-04e4-4d73-b29c-d2a5e60d5c8b',
    role: 'user',
    content: 'What is the difference between var, let, and const?',
    createdAt: new Date('2024-11-01T10:08:00Z'),
  },
  {
    id: '4d9f2a10-b7b5-4c72-8f4e-6b3c9d65e89a',
    role: 'assistant',
    content: 'var is function-scoped, while let and const are block-scoped. const is for variables that won’t be reassigned.',
    createdAt: new Date('2024-11-01T10:09:00Z'),
  },
  {
    id: '6f1e3b22-3a44-4b6a-9013-5c2e27f3a72b',
    role: 'user',
    content: 'Thanks! That clears it up. Can you suggest a good project idea for practice?',
    createdAt: new Date('2024-11-01T10:10:00Z'),
  },
  {
    id: '7b9c5d12-1c4a-43ea-b739-2c6e7b4f2b45',
    role: 'assistant',
    content: 'Sure! How about building a to-do list app with filtering and local storage?',
    createdAt: new Date('2024-11-01T10:11:00Z'),
  },
  {
    id: '8d7c4a21-5b94-48c7-83e9-1c7a6b2f2b74',
    role: 'user',
    content: 'That sounds great! Thanks for the suggestion.',
    createdAt: new Date('2024-11-01T10:12:00Z'),
  },
];


export default async function Page(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;
  const chat = {id: '1', userId: '1'};

  if (!chat) {
    notFound();
  }

  // const session = await auth();
  //
  // if (!session || !session.user) {
  //   return notFound();
  // }
  //
  // if (session.user.id !== chat.userId) {
  //   return notFound();
  // }

  const cookieStore = await cookies();
  const modelIdFromCookie = cookieStore.get('model-id')?.value;
  const selectedModelId =
    models.find((model) => model.id === modelIdFromCookie)?.id ||
    DEFAULT_MODEL_NAME;

  return (
    <PreviewChat
      id={'1'}
      initialMessages={fakeMessages}
      selectedModelId={selectedModelId}
    />
  );
}
