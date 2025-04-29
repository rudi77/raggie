// Custom EventEmitter implementation for browser
class EventEmitter {
  private events: { [key: string]: Function[] } = {};

  on(event: string, callback: Function): void {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }

  off(event: string, callback: Function): void {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  }

  emit(event: string, data?: any): void {
    if (!this.events[event]) return;
    this.events[event].forEach(callback => callback(data));
  }
}

interface WebSocketMessage {
  type: string;
  data?: any;
}

interface LiveUpdate {
  template_id: number;
  result: {
    timestamp: string;
    data: any;
    error?: string;
    template_info: {
      source_question: string;
      widget_type: string;
      refresh_rate: number;
    };
  };
}

class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000; // Start with 1 second
  private healthCheckInterval: number | null = null;
  private eventEmitter = new EventEmitter();

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
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/live`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.reconnectTimeout = 1000;
      this.startHealthCheck();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.stopHealthCheck();
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'live_update':
        this.eventEmitter.emit('live_update', message.data as LiveUpdate);
        break;
      case 'pong':
        // Health check response received
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  private startHealthCheck(): void {
    if (this.healthCheckInterval) {
      window.clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.sendMessage({ type: 'ping' });
      }
    }, 30000); // Send ping every 30 seconds
  }

  private stopHealthCheck(): void {
    if (this.healthCheckInterval) {
      window.clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    this.reconnectTimeout *= 2; // Exponential backoff

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, this.reconnectTimeout);
  }

  public sendMessage(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  public requestResults(): void {
    this.sendMessage({ type: 'get_results' });
  }

  public onLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.on('live_update', callback);
  }

  public offLiveUpdate(callback: (update: LiveUpdate) => void): void {
    this.eventEmitter.off('live_update', callback);
  }

  public disconnect(): void {
    this.stopHealthCheck();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const websocketService = WebSocketService.getInstance();
export type { LiveUpdate }; 