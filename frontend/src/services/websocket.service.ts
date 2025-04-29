import { EventEmitter } from './events';

// Add Vite env type definition
interface ImportMetaEnv {
  VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface WebSocketMessage {
  type: string;
  data?: any;
}

export interface LiveUpdate {
  template_id: number;
  result: {
    data: any;
    error?: string;
    timestamp: string;
  };
}

class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private eventEmitter = new EventEmitter();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000; // Start with 1 second
  private isConnecting = false;

  private constructor() {
    // Private constructor for singleton pattern
  }

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const backendHost = import.meta.env.VITE_API_URL || 'localhost:9000';
    const wsUrl = `${protocol}//${backendHost}/api/live`;

    console.log('Attempting to connect to WebSocket:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected successfully');
        this.reconnectAttempts = 0;
        this.reconnectTimeout = 1000;
        this.isConnecting = false;
        this.eventEmitter.emit('connected');
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnecting = false;
        this.eventEmitter.emit('disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.eventEmitter.emit('error', error);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle ping/pong
          if (data.type === 'ping') {
            console.debug('Received ping, sending pong');
            this.ws?.send(JSON.stringify({ type: 'pong' }));
            return;
          }
          
          // Handle template results
          if (data.type === 'template_result') {
            console.debug('Received template result:', data);
            this.eventEmitter.emit('live_update', data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      // Start heartbeat
      this.startHeartbeat();
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
      this.attemptReconnect();
    }
  }

  private startHeartbeat(): void {
    if (!this.ws) return;

    // Send ping every 30 seconds
    setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        console.debug('Sending ping');
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
      this.reconnectAttempts++;
      this.reconnectTimeout *= 2; // Exponential backoff
      this.connect();
    }, this.reconnectTimeout);
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public onLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.on('live_update', callback);
  }

  public offLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.off('live_update', callback);
  }

  public onConnected(callback: () => void): void {
    this.eventEmitter.on('connected', callback);
  }

  public offConnected(callback: () => void): void {
    this.eventEmitter.off('connected', callback);
  }

  public onDisconnected(callback: () => void): void {
    this.eventEmitter.on('disconnected', callback);
  }

  public offDisconnected(callback: () => void): void {
    this.eventEmitter.off('disconnected', callback);
  }

  public onError(callback: (error: any) => void): void {
    this.eventEmitter.on('error', callback);
  }

  public offError(callback: (error: any) => void): void {
    this.eventEmitter.off('error', callback);
  }
}

export const websocketService = WebSocketService.getInstance(); 