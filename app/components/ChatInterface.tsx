import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiImage, FiX } from 'react-icons/fi';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'system';
  type: 'text' | 'outfit' | 'color-analysis';
  timestamp: Date;
}

interface AgentStatus {
  name: string;
  status: string;
}

interface ChatInterfaceProps {
  onSendMessage: (message: string, userData: any) => Promise<void>;
  onUploadImage: (file: File) => Promise<void>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSendMessage,
  onUploadImage,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && !selectedImage) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      type: 'text',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);

    try {
      if (selectedImage) {
        await onUploadImage(selectedImage);
        setSelectedImage(null);
      } else {
        await onSendMessage(input, {});
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          content: '抱歉，發生錯誤。請稍後再試。',
          sender: 'system',
          type: 'text',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Agent Status Bar */}
      <div className="flex items-center justify-center p-4 bg-white border-b">
        <div className="flex space-x-4">
          {agentStatuses.map((agent) => (
            <div
              key={agent.name}
              className="flex items-center space-x-2"
            >
              <span className="text-lg">{agent.name}</span>
              <span
                className={`px-2 py-1 text-xs rounded-full ${
                  agent.status === 'analyzing'
                    ? 'bg-blue-100 text-blue-800'
                    : agent.status === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-green-100 text-green-800'
                }`}
              >
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-4 ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-800 shadow'
                }`}
              >
                {message.type === 'outfit' ? (
                  <div className="space-y-2">
                    <h3 className="font-semibold">穿搭建議</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Outfit cards would go here */}
                    </div>
                  </div>
                ) : message.type === 'color-analysis' ? (
                  <div className="space-y-2">
                    <h3 className="font-semibold">色彩分析</h3>
                    <div className="grid grid-cols-3 gap-2">
                      {/* Color swatches would go here */}
                    </div>
                  </div>
                ) : (
                  <p>{message.content}</p>
                )}
                <span className="text-xs opacity-70 mt-2 block">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        {selectedImage && (
          <div className="mb-4 relative">
            <img
              src={URL.createObjectURL(selectedImage)}
              alt="Selected"
              className="h-32 object-cover rounded-lg"
            />
            <button
              onClick={removeSelectedImage}
              className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full"
            >
              <FiX />
            </button>
          </div>
        )}
        <div className="flex space-x-4">
          <label className="cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <FiImage className="w-6 h-6 text-gray-500 hover:text-gray-700" />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="輸入您的訊息..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || (!input.trim() && !selectedImage)}
            className={`p-2 rounded-lg ${
              isLoading || (!input.trim() && !selectedImage)
                ? 'bg-gray-300'
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white`}
          >
            <FiSend className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 