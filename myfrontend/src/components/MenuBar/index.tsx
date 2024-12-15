import { randomInt } from "remirror";
import { useCallback } from "react";
import "remirror/styles/all.css";

import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { InvalidContentHandler } from "remirror";
import {
  BoldExtension,
  ItalicExtension,
  UnderlineExtension,
  FontSizeExtension,
  TextColorExtension, // Add TextColorExtension
  CollaborationExtension,
  YjsExtension,
} from "remirror/extensions";

import {
  Remirror,
  useRemirror,
  EditorComponent,
  OnChangeJSON,
} from "@remirror/react";

import MenuBar from "./MenuBar";

export interface Props {
  username: string;
}

const colors = [
  "#CC444B",
  "#32292F",
  "#8A4FFF",
  "#0B2027",
  "#F21B3F",
  "#FF9914",
  "#1F2041",
  "#4B3F72",
  "#FFC857",
];

const Editor: React.FC<Props> = (props) => {
  const { username } = props;

  const onError: InvalidContentHandler = useCallback(
    ({ json, invalidContent, transformers }: any) => {
      return transformers.remove(json, invalidContent);
    },
    []
  );

  const ydoc = new Y.Doc();
  const provider = new WebsocketProvider(
    "ws://localhost:8000/ws/editor/",
    "my-room",
    ydoc
  );

  provider.awareness.setLocalStateField("user", {
    name: username,
    color: colors[randomInt(0, colors.length - 1)],
  });

  const { manager, state, onChange } = useRemirror({
    extensions: () => [
      new BoldExtension(),
      new ItalicExtension(),
      new UnderlineExtension(),
      new FontSizeExtension({ defaultSize: "16", unit: "px" }),
      new TextColorExtension(), // Enable TextColorExtension here
      new CollaborationExtension({
        clientID: username,
      }),
      new YjsExtension({
        getProvider: () => provider,
      }),
    ],
    selection: "start",
    onError,
  });

  return (
    <div className="mt-2 mb-4">
      <Remirror
        manager={manager}
        initialContent={state}
        placeholder="Type Here."
        classNames={[
          "p-4 focus:outline-none h-96 overflow-y-auto scrollbar-hide prose lg:prose-xl prose-p:m-0",
        ]}
      >
        <MenuBar />
        <div className="rounded-md border">
          <EditorComponent />
          <OnChangeJSON onChange={onChange as any} />
        </div>
      </Remirror>
    </div>
  );
};

export default Editor;
