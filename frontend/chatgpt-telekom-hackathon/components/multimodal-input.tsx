'use client';

import type {
    Attachment,
    ChatRequestOptions,
    CreateMessage,
    Message,
} from 'ai';
import cx from 'classnames';
import {motion} from 'framer-motion';
import type React from 'react';
import {
    useRef,
    useEffect,
    useState,
    useCallback,
    type Dispatch,
    type SetStateAction,
    type ChangeEvent,
} from 'react';
import {toast} from 'sonner';
import {useLocalStorage, useWindowSize} from 'usehooks-ts';
import {Callout, Flex} from "@radix-ui/themes";


import {sanitizeUIMessages} from '@/lib/utils';

import {ArrowUpIcon, DocumentGlowIcon, PaperclipIcon, StopIcon} from './icons';
import {PreviewAttachment} from './preview-attachment';
import {Button} from './ui/button';
import {Textarea} from './ui/textarea';

export function MultimodalInput({
                                    chatId,
                                    input,
                                    setInput,
                                    isLoading,
                                    stop,
                                    attachments,
                                    setAttachments,
                                    messages,
                                    setMessages,
                                    append,
                                    handleSubmit,
                                    className,
                                    setPdfUrl,
                                }: {
    chatId: string;
    input: string;
    setInput: (value: string) => void;
    isLoading: boolean;
    stop: () => void;
    attachments: Array<Attachment>;
    setAttachments: Dispatch<SetStateAction<Array<Attachment>>>;
    messages: Array<Message>;
    setMessages: Dispatch<SetStateAction<Array<Message>>>;
    setPdfUrl: (url: string | null) => void;
    append: (
        message: Message | CreateMessage,
        chatRequestOptions?: ChatRequestOptions,
    ) => Promise<string | null | undefined>;
    handleSubmit: (
        event?: {
            preventDefault?: () => void;
        },
        chatRequestOptions?: ChatRequestOptions,
    ) => void;
    className?: string;
}) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const {width} = useWindowSize();
    const [selectedFiles, setSelectedFiles] = useState<Array<File>>([]);

    useEffect(() => {
        if (textareaRef.current) {
            adjustHeight();
        }
    }, []);

    const adjustHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight + 2}px`;
        }
    };

    const [localStorageInput, setLocalStorageInput] = useLocalStorage(
        'input',
        '',
    );

    useEffect(() => {
        if (textareaRef.current) {
            const domValue = textareaRef.current.value;
            // Prefer DOM value over localStorage to handle hydration
            const finalValue = domValue || localStorageInput || '';
            setInput(finalValue);
            adjustHeight();
        }
        // Only run once after hydration
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        setLocalStorageInput(input);
    }, [input, setLocalStorageInput]);

    const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(event.target.value);
        adjustHeight();
    };

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploadQueue, setUploadQueue] = useState<Array<string>>([]);

    useEffect(() => {
        console.log('Selected Files:', selectedFiles);
    }, [selectedFiles]);

    const handleFileChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);

        const pdfFiles = files.filter((file) => file.type === 'application/pdf');

        if (pdfFiles.length > 2) {
            toast.error('You can only upload a maximum of 2 PDFs!');
            return;
        }

        setSelectedFiles((prev) => {
            const newFiles = [...prev, ...files];
            if (newFiles.length > 2) {
                toast.error('You can only upload a maximum of 2 PDFs!');
                return prev;
            }
            return newFiles;
        });
    }, []);

    const submitForm = useCallback(async () => {
        if (selectedFiles.length !== 2) {
            toast.error('You must upload exactly 2 PDFs!');
            return;
        }

        const formData = new FormData();
        formData.append('user_document', selectedFiles[0]);
        formData.append('instruction_document', selectedFiles[1]);

        try {
            // Step 1: Upload PDFs to `/process_pdf`
            const pdfResponse = await fetch('http://localhost:8000/process_pdf', {
                method: 'POST',
                headers: { accept: 'application/pdf' },
                body: formData,
            });

            if (!pdfResponse.ok) {
                toast.error('PDF upload failed!');
                return;
            }

            // Extract the PDF blob
            const pdfBlob = await pdfResponse.blob();
            const pdfUrl = URL.createObjectURL(pdfBlob); // Create a URL for the PDF blob
            setPdfUrl(pdfUrl);
            // setAttachments((prev) => [
            //     ...prev,
            //     { url: pdfUrl, name: 'Processed PDF', contentType: 'application/pdf' },
            // ]);

            // Step 2: Send text input to `/chat`
            const chatResponse = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    accept: 'application/json',
                },
                body: JSON.stringify({
                    session_id: '1',
                    user_query: input,
                }),
            });

            if (chatResponse.ok) {
                const chatData = await chatResponse.json();

                const messageUser : Message = {
                    id: crypto.randomUUID(), // Generate a unique ID
                    role: 'user',
                    content: input,
                    createdAt: new Date(), // Set the current time
                };


                // Create a new Message object
                const newMessage : Message = {
                    id: crypto.randomUUID(), // Generate a unique ID
                    role: 'assistant',
                    content: chatData.response,
                    createdAt: new Date(), // Set the current time
                };


                // Update messages with the new message
                setMessages((prevMessages) => [...prevMessages, messageUser, newMessage]);

                toast.success('Message sent successfully!');
                console.log('Chat Response:', chatData);
                setInput(''); // Clear the input field
                setSelectedFiles([]); // Clear file selection and remove preview
            } else {
                const errorData = await chatResponse.json();
                toast.error(`Text submission failed: ${errorData.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            toast.error('An error occurred. Please try again.');
        }
    }, [selectedFiles, input, setInput, setMessages, setAttachments]);


    return (
        <div className="relative w-full flex flex-col gap-4">
            {selectedFiles.length > 0 && (
                <Flex gap="3">
                    {selectedFiles.map((file, index) => (
                        <Callout.Root size="2" key={index} className="rounded-2xl" color="gray" variant="soft">
                            <Callout.Icon>
                                <DocumentGlowIcon size={40}/>
                            </Callout.Icon>
                            <Callout.Text>
                                {file.name}
                            </Callout.Text>
                        </Callout.Root>
                    ))}
                </Flex>
            )}

            <input
                type="file"
                className="fixed -top-4 -left-4 size-0.5 opacity-0 pointer-events-none"
                ref={fileInputRef}
                multiple
                onChange={handleFileChange}
                tabIndex={-1}
            />

            {(attachments.length > 0 || uploadQueue.length > 0) && (
                <div className="flex flex-row gap-2 overflow-x-scroll items-end">
                    {attachments.map((attachment) => (
                        <PreviewAttachment key={attachment.url} attachment={attachment}/>
                    ))}

                    {uploadQueue.map((filename) => (
                        <PreviewAttachment
                            key={filename}
                            attachment={{
                                url: '',
                                name: filename,
                                contentType: '',
                            }}
                            isUploading={true}
                        />
                    ))}
                </div>
            )}

            <Textarea
                ref={textareaRef}
                placeholder="Send a message..."
                value={input}
                onChange={handleInput}
                className={cx(
                    'min-h-[24px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-3xl text-base dark:text-white bg-muted',
                    className,
                )}
                rows={3}
                autoFocus
                onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();

                        if (isLoading) {
                            toast.error('Please wait for the model to finish its response!');
                        } else {
                            submitForm();
                        }
                    }
                }}
            />

            {isLoading ? (
                <Button
                    className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
                    onClick={(event) => {
                        event.preventDefault();
                        stop();
                        setMessages((messages) => sanitizeUIMessages(messages));
                    }}
                >
                    <StopIcon size={14}/>
                </Button>
            ) : (
                <Button
                    className="rounded-full p-1.5 h-fit bg-[#E20074] hover:bg-[#c00063] drop-shadow-glow absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
                    onClick={(event) => {
                        event.preventDefault();
                        submitForm();
                    }}
                    disabled={selectedFiles.length !== 2 || uploadQueue.length > 0}
                >
                    <ArrowUpIcon size={14}/>
                </Button>
            )}

            <Button
                className="rounded-full p-1.5 h-fit absolute bottom-2 right-11 m-0.5 dark:border-zinc-700 dark:bg-transparent dark:hover:bg-gray-500"
                onClick={(event) => {
                    event.preventDefault();
                    fileInputRef.current?.click();
                }}
                variant="outline"
                disabled={isLoading || selectedFiles.length == 2}
            >
                <PaperclipIcon size={14}/>
            </Button>
        </div>
    );
}
