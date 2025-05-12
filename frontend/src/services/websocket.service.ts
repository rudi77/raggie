// Custom EventEmitter implementation for browser
class CustomEventEmitter {
  private listeners: {
    'live_update': ((data: LiveUpdate) => void)[];
    'connected': (() => void)[];
    'disconnected': (() => void)[];
    'error': ((error: Error) => void)[];
  } = {
    'live_update': [],
    'connected': [],
    'disconnected': [],
    'error': []
  };

  on(event: 'live_update', callback: (data: LiveUpdate) => void): void;
  on(event: 'connected' | 'disconnected', callback: () => void): void;
  on(event: 'error', callback: (error: Error) => void): void;
  on(event: string, callback: Function): void {
    if (event in this.listeners) {
      (this.listeners as any)[event].push(callback);
    }
  }

  off(event: 'live_update', callback: (data: LiveUpdate) => void): void;
  off(event: 'connected' | 'disconnected', callback: () => void): void;
  off(event: 'error', callback: (error: Error) => void): void;
  off(event: string, callback: Function): void {
    if (event in this.listeners) {
      (this.listeners as any)[event] = (this.listeners as any)[event].filter((cb: Function) => cb !== callback);
    }
  }

  emit(event: 'live_update', data: LiveUpdate): void;
  emit(event: 'connected' | 'disconnected'): void;
  emit(event: 'error', error: Error): void;
  emit(event: string, data?: any): void {
    if (event in this.listeners) {
      (this.listeners as any)[event].forEach((callback: Function) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }
}

// Environment variables type definition
interface ImportMetaEnv {
  readonly VITE_WS_URL: string;
  readonly VITE_WS_FALLBACK_URL?: string;
}

// Augment the ImportMeta interface
declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export interface LiveUpdate {
  template_id: number;
  template_info?: {
    name: string;
    description?: string;
    refresh_rate: number;
  };
  data: {
    sql_query: string;
    result: any[];
    answer: string;
  };
  error?: string;
  timestamp: string;
}

// Message type definitions
export type MessageType = 'ping' | 'pong' | 'get_results' | 'live_update';

interface BaseWebSocketMessage {
  type: MessageType;
}

interface PingMessage extends BaseWebSocketMessage {
  type: 'ping';
  timestamp: number;
}

interface PongMessage extends BaseWebSocketMessage {
  type: 'pong';
  timestamp: number;
}

interface GetResultsMessage extends BaseWebSocketMessage {
  type: 'get_results';
  query: string;
}

interface LiveUpdateMessage extends BaseWebSocketMessage {
  type: 'live_update';
  data: LiveUpdate;
}

type WebSocketMessage = PingMessage | PongMessage | GetResultsMessage | LiveUpdateMessage;

// WebSocket service class
export class WebSocketService {
  private static instance: WebSocketService;
  private socket: WebSocket | null = null;
  private eventEmitter = new CustomEventEmitter();
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 10;
  private readonly reconnectDelay = 2000;
  private heartbeatInterval: number | null = null;
  private lastPongTime: number = Date.now();
  private readonly maxMissedPongs = 5;
  private missedPongs = 0;
  private connectionCount = 0; // Track number of components using the connection

  private constructor() {
    // Private constructor for singleton
  }

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  public connect(url?: string): void {
    this.connectionCount++;
    
    // If we already have an open connection, just return
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    // If we have a connection in progress, wait for it
    if (this.socket?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const wsUrl = url || import.meta.env.VITE_WS_URL || 'ws://localhost:9000/api/live';
    if (!wsUrl) {
      this.emitError(new Error('No WebSocket URL provided'));
      return;
    }

    try {
      this.socket = new WebSocket(wsUrl);
      this.setupEventListeners();
    } catch (error) {
      this.emitError(error instanceof Error ? error : new Error('Failed to create WebSocket connection'));
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connection established');
      this.reconnectAttempts = 0;
      this.missedPongs = 0;
      this.eventEmitter.emit('connected');
      this.startHeartbeat();
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      this.eventEmitter.emit('disconnected');
      this.stopHeartbeat();
      this.attemptReconnect();
    };

    this.socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      this.emitError(new Error('WebSocket error occurred'));
    };

    this.socket.onmessage = (event) => {
      try {
        console.log('Received WebSocket message:', event.data);
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        this.emitError(new Error('Invalid message format'));
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('Handling WebSocket message:', message);
    switch (message.type) {
      case 'pong':
        console.log('Received pong message');
        this.handlePong();
        break;
      case 'live_update':
        console.log('Received live update:', message.data);
        this.eventEmitter.emit('live_update', message.data);
        break;
      default:
        console.log('Received unknown message type:', message.type);
        break;
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.sendMessage({
          type: 'ping',
          timestamp: Date.now()
        });
        
        // Check if we've missed too many pongs
        const now = Date.now();
        if (now - this.lastPongTime > 120000) { // Increased from 90 seconds to 120 seconds
          this.missedPongs++;
          if (this.missedPongs >= this.maxMissedPongs) {
            console.warn('Too many missed pongs, reconnecting...');
            this.disconnect();
            this.connect(); // Reconnect if we've missed too many pongs
          }
        }
      }
    }, 45000); // Increased from 30000 to 45000
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval !== null) {
      window.clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private handlePong(): void {
    this.lastPongTime = Date.now();
    this.missedPongs = 0;
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emitError(new Error('Max reconnection attempts reached'));
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    window.setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  public disconnect(): void {
    this.connectionCount--;
    
    // Only disconnect if no components are using the connection
    if (this.connectionCount <= 0) {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      this.stopHeartbeat();
      this.connectionCount = 0; // Ensure we don't go negative
    }
  }

  public sendMessage(message: WebSocketMessage): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message - WebSocket not connected');
      this.emitError(new Error('WebSocket is not connected'));
      return;
    }

    try {
      const messageStr = JSON.stringify(message);
      console.log('Sending WebSocket message:', messageStr);
      this.socket.send(messageStr);
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      this.emitError(error instanceof Error ? error : new Error('Failed to send message'));
    }
  }

  private emitError(error: Error): void {
    this.eventEmitter.emit('error', error);
  }

  // Convenience methods for live updates
  public onLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.on('live_update', callback);
  }

  public offLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.off('live_update', callback);
  }
}

export const websocketService = WebSocketService.getInstance(); 