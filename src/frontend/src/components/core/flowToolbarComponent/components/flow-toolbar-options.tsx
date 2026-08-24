import useFlowStore from "@/stores/flowStore";
import DeployButton from "./deploy-button";
import PublishDropdown from "./deploy-dropdown";
import PlaygroundButton from "./playground-button";
import ViewModeToggle from "./view-mode-toggle";

type FlowToolbarOptionsProps = {
  openApiModal: boolean;
  setOpenApiModal: (open: boolean | ((prev: boolean) => boolean)) => void;
};
const FlowToolbarOptions = ({
  openApiModal,
  setOpenApiModal,
}: FlowToolbarOptionsProps) => {
  const hasIO = useFlowStore((state) => state.hasIO);

  return (
    <div className="flex items-center gap-1">
      <ViewModeToggle />
      <div className="mx-1 h-6 w-px bg-border" />
      <PlaygroundButton hasIO={hasIO} />
      <PublishDropdown
        openApiModal={openApiModal}
        setOpenApiModal={setOpenApiModal}
      />
      <DeployButton />
    </div>
  );
};

export default FlowToolbarOptions;
