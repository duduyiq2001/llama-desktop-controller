import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

// Define types
interface ExecutionResult {
  success: boolean;
  message: string;
  output: string;
}

interface SystemResponse {
  command: string;
  generated_code: string;
  execution_result: ExecutionResult;
}

interface CommandHistoryItem {
  id: string;
  command: string;
  response: SystemResponse | null;
  timestamp: Date;
  status: 'success' | 'error' | 'pending';
}

// Type definition for SpeechRecognition API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

function App() {
  const API_URL = '/api'; // This will be proxied to http://localhost:5000
  const [command, setCommand] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [serviceStatus, setServiceStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [commandHistory, setCommandHistory] = useState<CommandHistoryItem[]>([]);
  const [isListening, setIsListening] = useState<boolean>(false);
  const commandInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Check if service is running on load
  useEffect(() => {
    checkServiceStatus();
    const interval = setInterval(checkServiceStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Setup speech recognition if available
  useEffect(() => {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setCommand(transcript);
        handleCommand(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const checkServiceStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`);
      if (response.status === 200) {
        setServiceStatus('online');
      } else {
        setServiceStatus('offline');
      }
    } catch (error) {
      console.error('Failed to check service status:', error);
      setServiceStatus('offline');
    }
  };

  const handleCommand = async (cmd: string) => {
    if (!cmd.trim()) return;
    
    // Generate a unique ID for this command
    const commandId = Date.now().toString();
    
    // Add to history as pending
    const historyItem: CommandHistoryItem = {
      id: commandId,
      command: cmd,
      response: null,
      timestamp: new Date(),
      status: 'pending'
    };
    
    setCommandHistory(prev => [historyItem, ...prev]);
    setIsProcessing(true);
    
    try {
      const response = await axios.post(`${API_URL}/process`, { command: cmd });
      const data: SystemResponse = response.data;
      
      // Update history with response
      setCommandHistory(prev => 
        prev.map(item => 
          item.id === commandId 
            ? { 
                ...item, 
                response: data, 
                status: data.execution_result.success ? 'success' : 'error' 
              } 
            : item
        )
      );
      
      // Clear command input on success
      setCommand('');
    } catch (error: any) {
      console.error('Error processing command:', error);
      
      // Update history with error
      setCommandHistory(prev => 
        prev.map(item => 
          item.id === commandId 
            ? { 
                ...item, 
                status: 'error',
                response: {
                  command: cmd,
                  generated_code: '# Failed to generate code',
                  execution_result: {
                    success: false,
                    message: error.message || 'Unknown error',
                    output: ''
                  }
                }
              } 
            : item
        )
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleCommand(command);
  };

  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      setIsListening(false);
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.start();
        setIsListening(true);
      }
    }
  };

  const isSpeechRecognitionAvailable = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;

  return (
    <div className="app-container">
      <header>
        <h1>MacOS LLM Controller</h1>
        <div className={`status-indicator ${serviceStatus}`}>
          Service: {serviceStatus}
        </div>
      </header>

      <form onSubmit={handleSubmit} className="command-form">
        <div className="input-container">
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Enter a command (e.g., 'open Safari')"
            disabled={isProcessing || serviceStatus !== 'online'}
            ref={commandInputRef}
          />
          {isSpeechRecognitionAvailable && (
            <button 
              type="button" 
              onClick={toggleListening}
              disabled={serviceStatus !== 'online'}
              className={isListening ? 'listening' : ''}
            >
              {isListening ? 'Listening...' : '🎤'}
            </button>
          )}
        </div>
        <button 
          type="submit" 
          disabled={!command.trim() || isProcessing || serviceStatus !== 'online'}
        >
          {isProcessing ? 'Processing...' : 'Execute'}
        </button>
      </form>

      <div className="command-history">
        <h2>Command History</h2>
        {commandHistory.length === 0 ? (
          <p className="no-history">No commands executed yet</p>
        ) : (
          <div className="history-list">
            {commandHistory.map((item) => (
              <div key={item.id} className={`history-item ${item.status}`}>
                <div className="command-text">
                  <strong>Command:</strong> {item.command}
                </div>
                <div className="timestamp">
                  {new Date(item.timestamp).toLocaleTimeString()}
                </div>
                
                {item.status === 'pending' ? (
                  <div className="loading">Processing...</div>
                ) : (
                  <div className="response-container">
                    {item.response && (
                      <>
                        <div className="code-container">
                          <strong>Generated Code:</strong>
                          <pre className="code-block">{item.response.generated_code}</pre>
                        </div>
                        <div className={`result ${item.response.execution_result.success ? 'success' : 'error'}`}>
                          <strong>Result:</strong> {item.response.execution_result.message}
                        </div>
                        {item.response.execution_result.output && (
                          <div className="output">
                            <strong>Output:</strong>
                            <pre>{item.response.execution_result.output}</pre>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;