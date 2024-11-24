export interface IElectronWindow {
  loadPreferences?: () => Promise<void>,
  windowClose: () => (void),
  windowMinimize: () => (void),
  windowMaximize: () => (void),
  transitionTo: (loc: string) => (void)
}

export interface ILandmarkerAPI {
    run: (userId: number, sequenceId: number, device=0) => (void),
    restart: (userId: number, sequenceId: number, device=0) => (void),
    stop: () => (void),
    play: () => (void),
    pause: () => (void),

    getScore: () => (Promise<Score>),
    getPoses: (sequenceId: number) => (Promise<Array<Poses>>),
    getAllHistory: () => (Promise<Array<any>>),
    getHistory: (sequenceId:number) => (Promise<Array<any>>),
    getPoseRecords: (sequenceId:number) => (Promise<Array<any>>),
    getSequenceData: (sequenceId: number) => (Promise<sequenceType>),
    recordHistory: (sessionId: number, score: number) => (Promise<Array<any>>),

    onSession: (callback: Function) => (void),
    onSessionDone: (callback: Function) => (void),
    onNextPose: (callback: Function) => (void),
    onFrame: (callback: Function) => (void),
    onStatus: (successCallback: Function, failCallback: Function)=>(void),
    enableRestart: (userId: number, sequenceId: number, restartListener:function)=>(void)
}

declare global {
  interface Window {
    landmarkerAPI: ILandmarkerAPI,
    electronWindow: IElectronWindow
  }
}