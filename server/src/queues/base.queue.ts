import { Queue, QueueEvents } from 'bullmq';
import logger from '#src/config/logger.ts';
import { bullmqConnection } from '#src/queues/bullmq.connection.ts';

const queuePrefix = process.env.BULLMQ_PREFIX || 'tryora';

export const createCustomQueue = <TData, TName extends string>(
  queueName: string,
  jobName: TName,
  defaultOptions: { attempts: number; backoff: number; keep: number }
) => {
  const queue = new Queue<TData, any, TName, TData, any, TName>(queueName, {
    connection: bullmqConnection,
    prefix: queuePrefix,
    defaultJobOptions: {
      attempts: defaultOptions.attempts,
      backoff: { type: 'exponential', delay: defaultOptions.backoff },
      removeOnComplete: { count: defaultOptions.keep },
      removeOnFail: { count: defaultOptions.keep * 2 },
    },
  });

  const events = new QueueEvents(queueName, {
    connection: bullmqConnection,
    prefix: queuePrefix,
  });
  events.on('error', err =>
    logger.error(`[BullMQ] ${queueName} error: ${err.message}`)
  );

  return {
    queue,
    events,
    add: (data: TData, jobId?: string) => queue.add(jobName, data, { jobId }),
    getState: async (jobId: string) =>
      (await queue.getJob(jobId))?.getState() || null,
    getCounts: () =>
      queue.getJobCounts('waiting', 'active', 'completed', 'failed', 'delayed'),
    pause: () => queue.pause(),
    resume: () => queue.resume(),
    close: () => Promise.all([queue.close(), events.close()]),
  };
};
