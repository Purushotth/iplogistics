import { BotService, BotResponse } from './bot-service';
import { BotDetails } from '../models/bot-details';
import { SessionsClient } from '@google-cloud/dialogflow-cx';
import { Readable } from 'stream';

jest.mock('@google-cloud/dialogflow-cx', () => {
  const originalModule = jest.requireActual('@google-cloud/dialogflow-cx');
  return {
    ...originalModule,
    SessionsClient: jest.fn().mockImplementation(() => ({
      projectLocationAgentSessionPath: jest.fn().mockReturnValue('test-session-path'),
      projectLocationAgentEnvironmentSessionPath: jest.fn().mockReturnValue('test-env-session-path'),
      streamingDetectIntent: jest.fn(() => {
        const stream: any = new Readable({ objectMode: true, read() {} });
        stream.write = jest.fn();
        stream.end = jest.fn();
        stream.on = jest.fn((event, cb) => {
          if (event === 'data') {
            cb({
              detectIntentResponse: {
                queryResult: {
                  responseMessages: [
                    { text: { text: ['Hello'] } }
                  ],
                  intentDetectionConfidence: 0.9,
                  parameters: { param1: 'value' }
                },
                outputAudio: new Uint8Array([1, 2, 3])
              }
            });
          }
        });
        return stream;
      }),
      detectIntent: jest.fn(() => Promise.resolve([{
        queryResult: {
          responseMessages: [
            { text: { text: ['Initial response'] } }
          ],
          intentDetectionConfidence: 1,
          parameters: { key: 'value' }
        },
        outputAudio: new Uint8Array([4, 5, 6])
      }]))
    }))
  };
});

const botDetails: BotDetails = {
  projectId: 'test-project',
  location: 'us-central1',
  agentId: 'agent-id',
  environment: 'draft',
  inputVariables: {},
  languageCode: 'en',
  outputAudioEncoding: 'OUTPUT_AUDIO_ENCODING_LINEAR_16',
  inputAudioEncoding: 'AUDIO_ENCODING_LINEAR_16',
  sampleRateHertz: 16000,
  initialEventName: 'WELCOME',
  outputVariables: {},
  DEFAULT_ENVIRONMENT: 'default'
};

const sessionDetails = {
  conversationId: 'conversation-id'
};

// Create a local instance for testing
let botService: BotService;

beforeEach(() => {
  botService = new BotService();
});

describe('BotService', () => {
  it('should create a new bot resource', async () => {
    const botResource = await botService.constructor.getBotIfExists(sessionDetails, botDetails);
    expect(botResource).toBeDefined();
  });

  it('should return initial bot response', async () => {
    const botResource = await botService.constructor.getBotIfExists(sessionDetails, botDetails);
    const response = await botResource.getInitialBotResponse();
    expect(response.text).toBe('Initial response');
    expect(response.confidence).toBe(1);
    expect(response.audioBytes).toBeInstanceOf(Uint8Array);
  });

  it('should return a response from streamed audio', async () => {
    const botResource = await botService.constructor.getBotIfExists(sessionDetails, botDetails);
    const data = new Uint8Array([10, 20, 30]);
    const response = await botResource.getBotResponse(data);
    expect(response.text).toBe('Hello');
    expect(response.confidence).toBe(0.9);
    expect(response.audioBytes).toBeInstanceOf(Uint8Array);
  });

  it('should support fluent API on BotResponse', () => {
    const response = new BotResponse('match', 'text')
      .withConfidence(0.95)
      .withAudioBytes(new Uint8Array([1, 2]))
      .withEndSession(true);

    expect(response.confidence).toBe(0.95);
    expect(response.audioBytes).toEqual(new Uint8Array([1, 2]));
    expect(response.endSession).toBe(true);
  });
});
