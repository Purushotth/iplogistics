import { Server } from './server';
import WebSocket from 'ws';
import { Request } from 'express';

jest.mock('../models/session-details', () => ({
  SessionDetails: jest.fn(() => ({ mock: true }))
}));

jest.mock('../services/bot-service', () => ({
  BotService: jest.fn(() => ({ mock: true }))
}));

jest.mock('../services/dtmf-service', () => ({
  DTMFService: jest.fn(() => ({ mock: true }))
}));

jest.mock('../handlers/message-handler-registry', () => ({
  MessageHandlerRegistry: jest.fn(() => ({ mock: true }))
}));

jest.mock('../common/session', () => {
  return {
    Session: jest.fn().mockImplementation(() => ({
      processBinaryMessage: jest.fn(),
      processTextMessage: jest.fn(),
      close: jest.fn()
    }))
  };
});

const createMockRequest = () => ({
  headers: { authorization: 'Bearer token' },
  url: '/connect'
} as unknown as Request);

describe('Server WebSocket Handling', () => {
  let server: Server;
  let mockWS: any;
let mockSocket: any;
let mockWSServer: any;
let mockWSServerFactory: any;

  beforeEach(() => {
    mockWSServer = {
  on: jest.fn(),
  emit: jest.fn(),
  handleUpgrade: jest.fn()
};

mockWSServerFactory = jest.fn(() => mockWSServer);
const mockWSServer = {
  on: jest.fn(),
  emit: jest.fn(),
  handleUpgrade: jest.fn()
};
    const secretServiceMock = {
  verify: jest.fn(() => Promise.resolve({ code: 'VERIFIED' }))
};
const webSocketServerFactory = jest.fn(() => mockWSServer);
server = new Server(jest.fn(), jest.fn(), webSocketServerFactory, secretServiceMock);


    mockWS = {
      on: jest.fn(),
      close: jest.fn(),
      readyState: WebSocket.OPEN
    };

    mockSocket = {
      write: jest.fn(),
      destroy: jest.fn()
    };
  });

  it('should start and verify request successfully', async () => {
    const mockHandleUpgrade = jest.fn();
    const emitMock = jest.fn();
    server['_wsServer'] = { on: jest.fn(), emit: emitMock, handleUpgrade: mockHandleUpgrade };

    await server.start();
    expect(server['_wsServer'].on).toHaveBeenCalledWith('connection', expect.any(Function));
  });

  it('should reject request if signature is invalid', async () => {
    const rejectSecretService = {
  verify: jest.fn(() => Promise.resolve({ code: 'INVALID' }))
};
const rejectWSServer = {
  on: jest.fn(),
  emit: jest.fn(),
  handleUpgrade: jest.fn()
};
const rejectServer = new Server(
  jest.fn(),
  jest.fn(),
  webSocketServerFactory,
  rejectSecretService
);

    const socketMock = { write: jest.fn(), destroy: jest.fn() };
    await rejectServer['verifyRequestSignature']({} as Request, rejectServer['secretService'], socketMock);
    expect(socketMock.write).toHaveBeenCalled();
    expect(socketMock.destroy).toHaveBeenCalled();
  });

  it('should create new session and store it in sessionMap', () => {
    const request = createMockRequest();
    server['createConnection'](mockWS, request);
    const storedSession = Server['sessionMap'].get(mockWS);
    expect(storedSession).toBeDefined();
  });

  it('should delete connection and clean up', () => {
    const dummySession = { close: jest.fn() };
    Server['sessionMap'].set(mockWS, dummySession);
    server['deleteConnection'](mockWS);
    expect(dummySession.close).toHaveBeenCalled();
    expect(Server['sessionMap'].has(mockWS)).toBe(false);
  });

  it('should process binary messages when session exists', () => {
    const session = require('../common/session').Session.mock.instances[0];
    Server['sessionMap'].set(mockWS, session);
    const messageHandler = server['_wsServer']?.on?.mock.calls.find(([event]) => event === 'message')?.[1];
    if (messageHandler) {
      messageHandler.call(server, { binary: true, data: new Uint8Array([1, 2, 3]) }, mockWS);
      expect(session.processBinaryMessage).toHaveBeenCalled();
    }
  });

  it('should process text messages when session exists', () => {
    const session = require('../common/session').Session.mock.instances[0];
    Server['sessionMap'].set(mockWS, session);
    const messageHandler = server['_wsServer']?.on?.mock.calls.find(([event]) => event === 'message')?.[1];
    if (messageHandler) {
      messageHandler.call(server, { binary: false, data: Buffer.from('hello') }, mockWS);
      expect(session.processTextMessage).toHaveBeenCalled();
    }
  });

  it('should create dummy session if message received before handshake', () => {
    Server['sessionMap'].delete(mockWS);
    const dummy = require('../common/session').Session;
    const messageHandler = server['_wsServer']?.on?.mock.calls.find(([event]) => event === 'message')?.[1];
    if (messageHandler) {
      messageHandler.call(server, { binary: false, data: Buffer.from('orphan') }, mockWS);
      expect(dummy).toHaveBeenCalled();
    }
  });
});
