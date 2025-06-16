import { BotService, BotResource, BotResponse, SessionDetails, BotDetails } from './bot-service';
import { protos, SessionsClient } from '@google-cloud/dialogflow-cx';
import { Readable } from 'stream';

jest.mock('@google-cloud/dialogflow-cx', () => {
  const original = jest.requireActual('@google-cloud/dialogflow-cx');
  return {
    ...original,
    SessionsClient: jest.fn().mockImplementation(() => ({
      projectLocationAgentSessionPath: jest.fn(() => 'projects/p/locations/l/agents/a/sessions/s'),
      projectLocationAgentEnvironmentSessionPath: jest.fn(() => 'projects/p/locations/l/agents/a/environments/e/sessions/s'),
      detectIntent: jest.fn().mockResolvedValue([{
        queryResult: {
          responseMessages: [
            { text: { text: ['Hi there!'] } }
          ],
          intentDetectionConfidence: 0.88,
          parameters: { key: 'val' }
        },
        outputAudio: new Uint8Array([1, 2, 3])
      }]),
      streamingDetectIntent: jest.fn(() => {
        const s: any = new Readable({ objectMode: true, read() {} });
        s.write = jest.fn();
        s.end = jest.fn();
        s.on = jest.fn((event, cb) => {
          if (event === 'data') {
            cb({
              detectIntentResponse: {
                queryResult: {
                  responseMessages: [
                    { text: { text: ['Streamed response'] } }
                  ],
                  intentDetectionConfidence: 0.9,
                  parameters: { a: 1 }
                },
                outputAudio: new Uint8Array([4, 5, 6])
              }
            });
          }
        });
        return s;
      })
    }))
  }
});


const sessionDetails: SessionDetails = {
  organizationId: 'org1',
  correlationId: 'corr1',
  sessionId: 'sess1',
  conversationId: 'conv1'
};

const botDetails: BotDetails = {
  projectId: 'proj1',
  location: 'us-central1',
  agentId: 'agent1',
  environment: 'draft',
  inputVariables: { foo: 'bar' },
  languageCode: 'en',
  outputAudioEncoding: protos.google.cloud.dialogflow.cx.v3.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
  inputAudioEncoding: protos.google.cloud.dialogflow.cx.v3.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
  sampleRateHertz: 16000,
  initialEventName: 'WELCOME',
  outputVariables: {} // ensure this is defined to avoid undefined access errors
};

describe('BotService and BotResource Integration', () => {
  it('should create and return a BotResource instance', async () => {
    const resource = await BotService.getBotIfExists(sessionDetails, botDetails);
    expect(resource).toBeInstanceOf(BotResource);
  });

  it('should return valid initial response from detectIntent', async () => {
    const resource = await BotService.getBotIfExists(sessionDetails, botDetails);
    const response = await resource.getInitialBotResponse();
    expect(response.text).toBe('Hi there!');
    expect(response.audioBytes).toBeInstanceOf(Uint8Array);
    expect(response.confidence).toBeCloseTo(0.88);
  });

  it('should return valid response from streamingDetectIntent', async () => {
    const resource = await BotService.getBotIfExists(sessionDetails, botDetails);
    const response = await resource.getBotResponse(new Uint8Array([10, 20]));
    expect(response.text).toBe('Streamed response');
    expect(response.audioBytes).toBeInstanceOf(Uint8Array);
    expect(response.confidence).toBeCloseTo(0.9);
  });
});

describe('BotResponse Fluent API', () => {
  it('should chain configuration properly', () => {
    const result = new BotResponse('match', 'message')
      .withConfidence(0.7)
      .withAudioBytes(new Uint8Array([9, 8]))
      .withEndSession(true);

    expect(result.confidence).toBe(0.7);
    expect(result.audioBytes).toEqual(new Uint8Array([9, 8]));
    expect(result.endSession).toBe(true);
  });
});
