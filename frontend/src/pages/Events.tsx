/* eslint-disable @typescript-eslint/no-unused-vars */
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import dayjs, { Dayjs } from "dayjs";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import ServerDown from "svg/undraw/server_down.svg?react";
import "video.js/dist/video-js.css";

import { ErrorMessage } from "components/error/ErrorMessage";
import { Layout, LayoutSmall } from "components/events/Layouts";
import { Loading } from "components/loading/Loading";
import { useTitle } from "hooks/UseTitle";
import { useCameras } from "lib/api/cameras";
import { insertURLParameter } from "lib/helpers";
import * as types from "lib/types";

const Events = () => {
  useTitle("Events");
  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up("sm"));
  const [searchParams] = useSearchParams();
  const cameraQuery = useCameras({});
  const [selectedCamera, setSelectedCamera] = useState<types.Camera | null>(
    null,
  );
  const [selectedRecording, setSelectedRecording] =
    useState<types.Recording | null>(null);
  const [date, setDate] = useState<Dayjs | null>(
    searchParams.has("date")
      ? dayjs(searchParams.get("date") as string)
      : dayjs(),
  );
  const [source, setSource] = useState<string | null>(null);

  const changeSelectedCamera = (
    ev: React.MouseEvent<HTMLButtonElement, MouseEvent>,
    camera: types.Camera,
  ) => {
    setSelectedCamera(camera);
  };

  useEffect(() => {
    if (cameraQuery.data && searchParams.has("camera") && !selectedCamera) {
      setSelectedCamera(cameraQuery.data[searchParams.get("camera") as string]);
    }
  }, [cameraQuery.data, searchParams, selectedCamera]);
  useEffect(() => {
    if (selectedCamera) {
      insertURLParameter("camera", selectedCamera.identifier);
    }
  }, [selectedCamera]);
  useEffect(() => {
    if (date) {
      insertURLParameter("date", date.format("YYYY-MM-DD"));
    }
  }, [date]);

  if (cameraQuery.isError) {
    return (
      <ErrorMessage
        text={`Error loading cameras`}
        subtext={cameraQuery.error.message}
        image={
          <ServerDown
            width={150}
            height={150}
            role="img"
            aria-label="Server down"
          />
        }
      />
    );
  }

  if (cameraQuery.isLoading) {
    return <Loading text="Loading Camera" />;
  }

  if (!cameraQuery.data) {
    return null;
  }

  if (matches) {
    return (
      <Layout
        cameras={cameraQuery.data}
        selectedCamera={selectedCamera}
        selectedRecording={selectedRecording}
        setSelectedRecording={setSelectedRecording}
        changeSelectedCamera={changeSelectedCamera}
        date={date}
        setDate={setDate}
        setSource={setSource}
      />
    );
  }
  return (
    <LayoutSmall
      cameras={cameraQuery.data}
      selectedCamera={selectedCamera}
      selectedRecording={selectedRecording}
      setSelectedRecording={setSelectedRecording}
      changeSelectedCamera={changeSelectedCamera}
      date={date}
      setDate={setDate}
      setSource={setSource}
    />
  );
};

export default Events;