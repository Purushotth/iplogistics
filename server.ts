import { Server } from '../src/websocket/server';
import { Express } from 'express';
import WebSocket, { WebSocketServer } from 'ws';
import http from 'http';

import { verifyRequestSignature } from '../src/auth/authenticator';
import { Session } from '../src/common/session';
import { BotService } from '../src/services/bot-service';
import { DTMFService } from '../src/services/dtmf-service';
import { MessageHandlerRegistry } from '../src/services/message-handler-registry';
import { SessionDetails } from '../src/models/session-details';
import { SecretService } from '../src/services/secret-service';

jest.mock('../src/auth/authenticator');
jest.mock('../src/common/session');

describe('Server', () => {
  let mockExpress: jest.Mocked<Express>;
  let mockHttpServer: http.Server;
  let mockWSServer: WebSocketServer;
  let mockSecretService: SecretService;
  let mockRequest: any;
  let mockSocket: any;
  let server: Server;

  beforeEach(() => {
    mockExpress = {} as any;
    mockHttpServer = {} as any;
    mockWSServer = {
      on: jest.fn(),
      handleUpgrade: jest.fn(),
      emit: jest.fn()
    } as any;
    mockSecretService = {
      getSecretForKey: jest.fn()
    } as any;

    server = new Server(
      () => mockExpress,
      () => mockHttpServer,
      () => mockWSServer,
      mockSecretService
    );

    mockRequest = { headers: { 'x-api-key': 'test' }, url: '/test' };
    mockSocket = {
      write: jest.fn(),
      destroy: jest.fn()
    };
  });

  it('should start the server and bind WebSocket events', async () => {
    (verifyRequestSignature as jest.Mock).mockResolvedValue({ code: 'VERIFIED' });

    server.start();

    const upgradeHandler = (mockWSServer.on as jest.Mock).mock.calls.find(call => call[0] === 'connection');
    expect(mockWSServer.on).toHaveBeenCalledWith('connection', expect.any(Function));
    expect(upgradeHandler).toBeDefined();
  });

  it('should reject connection if signature is not VERIFIED', async () => {
    (verifyRequestSignature as jest.Mock).mockResolvedValue({ code: 'INVALID' });

    await (server as any)._wsServer.on.mock.calls[0][1](mockRequest, mockSocket, {}); // simulate upgrade

    expect(mockSocket.write).toHaveBeenCalledWith(expect.stringContaining('401 Unauthorized'));
    expect(mockSocket.destroy).toHaveBeenCalled();
  });

  it('should handle WebSocket connection and message', async () => {
    const ws = {
      on: jest.fn(),
      readyState: WebSocket.OPEN,
      close: jest.fn()
    } as any;

    const mockSession = {
      processBinaryMessage: jest.fn(),
      processTextMessage: jest.fn()
    };

    (Session as jest.Mock).mockImplementation(() => mockSession);

    server.start();
    const connectionHandler = (mockWSServer.on as jest.Mock).mock.calls.find(call => call[0] === 'connection')[1];

    connectionHandler(ws, mockRequest);

    const messageHandler = (ws.on as jest.Mock).mock.calls.find(call => call[0] === 'message')[1];

    // Handle binary
    messageHandler(Buffer.from([0x01, 0x02]), true);
    expect(mockSession.processBinaryMessage).toHaveBeenCalled();

    // Handle text
    messageHandler(Buffer.from('hello'), false);
    expect(mockSession.processTextMessage).toHaveBeenCalled();
  });

  it('should handle WebSocket close and cleanup session', () => {
    const ws = {
      on: jest.fn(),
      close: jest.fn()
    } as any;

    const closeFn = jest.fn();
    const mockSession = { close: closeFn };

    (Session as jest.Mock).mockImplementation(() => mockSession);

    (server as any).constructor['sessionMap'].set(ws, mockSession);

    server['deleteConnection'](ws);
    expect(closeFn).toHaveBeenCalled();
  });
});
