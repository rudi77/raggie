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
  result: {
    data: unknown;
    error?: string;
    timestamp: string;
  };
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
  private readonly maxReconnectAttempts = 5;
  private readonly reconnectDelay = 1000;
  private heartbeatInterval: number | null = null;
  private lastPongTime: number = Date.now();
  private readonly maxMissedPongs = 3;
  private missedPongs = 0;

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
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = url || import.meta.env.VITE_WS_URL || 'ws://localhost:5173/api/live';
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
      this.reconnectAttempts = 0;
      this.missedPongs = 0;
      this.eventEmitter.emit('connected');
      this.startHeartbeat();
    };

    this.socket.onclose = () => {
      this.eventEmitter.emit('disconnected');
      this.stopHeartbeat();
      this.attemptReconnect();
    };

    this.socket.onerror = (event) => {
      this.emitError(new Error('WebSocket error occurred'));
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch (error) {
        this.emitError(new Error('Invalid message format'));
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'pong':
        this.handlePong(message);
        break;
      case 'live_update':
        this.eventEmitter.emit('live_update', message.data);
        break;
      default:
        // We don't emit other message types
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
        if (now - this.lastPongTime > 90000) { // 90 seconds
          this.missedPongs++;
          if (this.missedPongs >= 3) {
            this.disconnect();
            this.connect(); // Reconnect if we've missed too many pongs
          }
        }
      }
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval !== null) {
      window.clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private handlePong(message: PongMessage): void {
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
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.stopHeartbeat();
  }

  public sendMessage(message: WebSocketMessage): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.emitError(new Error('WebSocket is not connected'));
      return;
    }

    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
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