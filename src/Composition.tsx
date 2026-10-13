import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type Props = {
  title: string;
  subtitle: string;
};

const calculateMetadata: CalculateMetadataFunction<Props> = () => {
  return {};
};

export const MyComposition = () => {
  return (
    <Composition
      id="MyComp"
      component={MyComponent}
      durationInFrames={120}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        title: "Olá, Remotion!",
        subtitle: "Vídeos feitos com React",
      }}
      calculateMetadata={calculateMetadata}
    />
  );
};

export const MyComponent: React.FC<Props> = ({ title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleIn = spring({ frame, fps, config: { damping: 200 } });
  const subtitleIn = spring({
    frame: frame - 15,
    fps,
    config: { damping: 200 },
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0b1020",
        justifyContent: "center",
        alignItems: "center",
        padding: "100px 80px",
        fontFamily: "Inter, Helvetica, Arial, sans-serif",
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          color: "white",
          fontSize: 110,
          fontWeight: 800,
          textAlign: "center",
          lineHeight: 1.1,
          opacity: titleIn,
          transform: `translateY(${interpolate(titleIn, [0, 1], [60, 0])}px)`,
        }}
      >
        {title}
      </div>
      <div
        style={{
          marginTop: 40,
          color: "#8fa8ff",
          fontSize: 52,
          fontWeight: 500,
          textAlign: "center",
          opacity: subtitleIn,
          transform: `translateY(${interpolate(subtitleIn, [0, 1], [40, 0])}px)`,
        }}
      >
        {subtitle}
      </div>
    </AbsoluteFill>
  );
};
