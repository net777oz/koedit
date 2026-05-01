/* eslint-disable @typescript-eslint/no-explicit-any */
import nipple from "nipplejs";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "preact/hooks";
import { Dropbox } from "dropbox";
import { createDos, applyMove } from "../dos/create-dos";
import { createIdbFileSystem } from "../fs/create-idb-file-system";
import { detectFileChange } from "../fs/detect-file-change";
import { VirtualKeyboard } from "./VirtualKeyboard.tsx";

const JOYSTICK_MAPS = [
  105, // ArrowRightUp
  104, // ArrowUp
  103, // ArrowLeftUp
  100, // ArrowLeft
  97, // ArrowLeftDown
  98, // ArrowDown
  99, // ArrowRightDown
  102, // ArrowRight
];

export interface GameConfig {
  gameFile?: string; // water2.zip
  mod?: string; // water2
  entry?: string; // KOEI.COM
  saveFile?: string; // KOUKAI2.DAT
}

export interface GameProps {
  config: GameConfig;
  dbx?: Dropbox;
}

type EventHandler = (e: KeyboardEvent) => void;

function getBlockedHandler(target: EventTarget, type: string): EventHandler[] {
  return (target as any)._blockedHandlers?.[type] || [];
}

function restoreAddEventListener(target: EventTarget) {
  if ((target as any)._addEventListener) {
    target.addEventListener = (target as any)._addEventListener;
  }
}

function blockAddEventListener(target: EventTarget, types: string[]) {
  if (!(target as any)._addEventListener) {
    (target as any)._addEventListener = target.addEventListener;
  }

  if (!(target as any)._blockedHandlers) {
    (target as any)._blockedHandlers = {};
  }

  target.addEventListener = (type: string, handler: any, options?: any) => {
    if (types.includes(type)) {
      if (!(target as any)._blockedHandlers[type]) {
        (target as any)._blockedHandlers[type] = [];
      }
      (target as any)._blockedHandlers[type].push(handler);
    } else {
      (target as any)._addEventListener(type, handler, options);
    }
  };
}

export function Game({
  config: {
    gameFile = "water2.zip",
    mod = "water2",
    entry = "KOEI.COM",
    saveFile = "KOUKAI2.DAT",
  },
  dbx,
}: GameProps) {
  const [width, setWidth] = useState(640);
  const [height, setHeight] = useState(480);

  const [joystickCode, setJoystickCode] = useState<number | null>(null);
  const joystickCodeBefore = useRef<number | null>(null);

  const [enabledToggleFns, setEnabledToggleFns] = useState(false);
  const [enabledToggleFullscreen, setEnabledToggleFullscreen] = useState(false);
  const [enabledToggleKeyboard, setEnabledToggleKeyboard] = useState(true);

  const screen = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const mobileController = useRef<HTMLDivElement>(null);

  const isClearExit = useRef(false);

  const database = useRef<any>();
  const keydownHandlers = useRef<EventHandler[]>([]);
  const keyupHandlers = useRef<EventHandler[]>([]);

  const [toastMessage, setToastMessage] = useState<string | undefined>();
  const [innerToastMessage, setInnerToastMessage] = useState<string | undefined>();

  useEffect(() => {
    if (toastMessage) {
      setInnerToastMessage(toastMessage);
      const timeout = setTimeout(() => {
        setToastMessage(undefined);
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [toastMessage]);

  const resetGame = useCallback(
    async (isFsClear = false) => {
      if (
        window.confirm(
          isFsClear
            ? "에뮬레이터를 완전히 초기화하시겠습니까? (캐시된 게임 파일이 모두 삭제됩니다)"
            : "진행 중인 모든 데이터를 삭제하시겠습니까?",
        )
      ) {
        if (isFsClear) {
          await database.current?.clear();
          localStorage.clear();
        } else {
          await database.current?.delete(saveFile);
        }
        window.location.reload();
      }
    },
    [saveFile],
  );

  const start = useCallback(async () => {
    const joystick = nipple.create({
      zone: mobileController.current!,
    });

    blockAddEventListener(document, ["keydown", "keyup", "keypress"]);

    const db = (database.current = await createIdbFileSystem(mod, 1));
    const { fs, main } = await createDos(canvas.current!);

    await fs.extract(`/static/game/${gameFile}?v=${Date.now()}`);

    const saveFileBody = await db.load(saveFile);
    if (saveFileBody) {
      (fs as any).fs.writeFile(saveFile, saveFileBody);
    }

    await main(["-c", entry]);

    keydownHandlers.current = getBlockedHandler(document, "keydown");
    keyupHandlers.current = getBlockedHandler(document, "keyup");
    restoreAddEventListener(document);

    document.addEventListener("keydown", (e) => {
      keydownHandlers.current.forEach((handler) => handler(e));
    });
    document.addEventListener("keyup", (e) => {
      keyupHandlers.current.forEach((handler) => handler(e));
    });

    joystick.on("move", (_, data) => {
      if (data.force > 0.3) {
        setJoystickCode(JOYSTICK_MAPS[(Math.floor((data.angle.degree - 22.5) / 45) + 8) % 8]);
      }
    });

    joystick.on("end", () => {
      setJoystickCode(null);
    });

    return () => {
      main.exit();
    };
  }, [gameFile, mod, entry, saveFile]);

  useEffect(() => {
    start();
  }, [start]);

  return (
    <div class="game">
      <div
        class="game__screen"
        style={{ width: `${width}px`, height: `${height}px` }}
        ref={screen}
      >
        <div class="game__canvas">
          <canvas ref={canvas} />
        </div>
        <div class="game__event-blocker" ref={mobileController} />
        {enabledToggleKeyboard && <VirtualKeyboard onKeyDown={() => {}} onKeyUp={() => {}} />}
      </div>
      <div class={`toast ${toastMessage ? "toast--active" : ""}`}>{innerToastMessage}</div>
    </div>
  );
}
