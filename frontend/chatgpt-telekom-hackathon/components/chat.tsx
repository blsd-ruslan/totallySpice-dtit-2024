'use client';

import type { Attachment, Message } from 'ai';
import { useChat } from 'ai/react';
import { AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { useWindowSize } from 'usehooks-ts';

import { ChatHeader } from '@/components/chat-header';
import { PreviewMessage, ThinkingMessage } from '@/components/message';
import { useScrollToBottom } from '@/components/use-scroll-to-bottom';

import { Block, type UIBlock } from './block';
import { BlockStreamHandler } from './block-stream-handler';
import { MultimodalInput } from './multimodal-input';
import { Overview } from './overview';
import PDFViewer from "@/components/pdf-viewer";
import {Flex} from "@radix-ui/themes";
import {Card} from "@/components/ui/card";

export function Chat({
  id,
  initialMessages,
  selectedModelId,
}: {
  id: string;
  initialMessages: Array<Message>;
  selectedModelId: string;
}) {
  const {
    messages,
    setMessages,
    handleSubmit,
    input,
    setInput,
    append,
    isLoading,
    stop,
    data: streamingData,
  } = useChat({
    body: { id, modelId: selectedModelId },
    initialMessages,
  });

  const { width: windowWidth = 1920, height: windowHeight = 1080 } =
    useWindowSize();

  const [block, setBlock] = useState<UIBlock>({
    documentId: 'init',
    content: '',
    title: '',
    status: 'idle',
    isVisible: false,
    boundingBox: {
      top: windowHeight / 4,
      left: windowWidth / 4,
      width: 250,
      height: 50,
    },
  });

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();
  const [attachments, setAttachments] = useState<Array<Attachment>>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  return (
    <>
      <div className="flex mx-8 flex-col min-w-0 h-dvh bg-background">
        <ChatHeader selectedModelId={selectedModelId} />
        <div
          ref={messagesContainerRef}
          className="flex flex-col min-w-0 flex-1 overflow-y-scroll pt-4"
        >
          {messages.length === 0 && <Overview />}

          {messages.length > 0 && (
              <Flex gap="3">
                <Card
                    className='p-2 rounded-2xl border-2 border-solid flex flex-col h-[700px]'
                >
                  <div
                      style={{
                        overflowY: 'auto',  // Enable vertical scrolling
                        padding: '1rem',    // Optional: Add some padding for better appearance
                      }}
                      className='overflow-y-auto rounded-2xl space-y-4'
                  >
                    {messages.map((message, index) => (
                        <PreviewMessage
                            key={message.id}
                            chatId={id}
                            message={message}
                            block={block}
                            setBlock={setBlock}
                            isLoading={isLoading && messages.length - 1 === index}
                        />
                    ))}
                  </div>
                </Card>

                {pdfUrl &&
                    <PDFViewer
                        pdfUrl={pdfUrl}
                        title="Analyzed Document"
                    />
                }
              </Flex>
          )
          }


          {isLoading &&
              messages.length > 0 &&
              messages[messages.length - 1].role === 'user' && (
                  <ThinkingMessage/>
              )}

          <div
              ref={messagesEndRef}
              className="shrink-0 min-w-[24px] min-h-[24px]"
          />
        </div>
        <form className="flex mx-auto mt-4 px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
          <MultimodalInput
              chatId={id}
              input={input}
              setInput={setInput}
              handleSubmit={handleSubmit}
              isLoading={isLoading}
              stop={stop}
              attachments={attachments}
              setAttachments={setAttachments}
              messages={messages}
              setMessages={setMessages}
              setPdfUrl={setPdfUrl}
              append={append}
          />
        </form>
      </div>

      <AnimatePresence>
        {block?.isVisible && (
          <Block
            chatId={id}
            input={input}
            setInput={setInput}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
            stop={stop}
            attachments={attachments}
            setAttachments={setAttachments}
            append={append}
            block={block}
            setBlock={setBlock}
            messages={messages}
            setMessages={setMessages}
          />
        )}
      </AnimatePresence>

      <BlockStreamHandler streamingData={streamingData} setBlock={setBlock} />
    </>
  );
}
