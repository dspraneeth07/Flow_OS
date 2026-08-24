import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { HelpDropdownView } from "@/components/core/canvasControlsComponent/HelpDropdownView";
import { DATASTAX_DOCS_URL, DOCS_URL } from "@/constants/constants";
import { ENABLE_DATASTAX_FLOWOS } from "@/customization/feature-flags";
import useFlowStore from "@/stores/flowStore";

const HelpDropdown = () => {
  const navigate = useNavigate();
  const [isHelpMenuOpen, setIsHelpMenuOpen] = useState(false);
  const helperLineEnabled = useFlowStore((state) => state.helperLineEnabled);
  const setHelperLineEnabled = useFlowStore(
    (state) => state.setHelperLineEnabled,
  );
  const inspectionPanelVisible = useFlowStore(
    (state) => state.inspectionPanelVisible,
  );
  const setInspectionPanelVisible = useFlowStore(
    (state) => state.setInspectionPanelVisible,
  );

  const onToggleHelperLines = useCallback(() => {
    setHelperLineEnabled(!helperLineEnabled);
  }, [helperLineEnabled]);

  const onToggleInspectionPanel = useCallback(() => {
    setInspectionPanelVisible(!inspectionPanelVisible);
  }, [inspectionPanelVisible]);

  const docsUrl = ENABLE_DATASTAX_FLOWOS ? DATASTAX_DOCS_URL : DOCS_URL;

  return (
    <HelpDropdownView
      isOpen={isHelpMenuOpen}
      onOpenChange={setIsHelpMenuOpen}
      helperLineEnabled={helperLineEnabled}
      onToggleHelperLines={onToggleHelperLines}
      inspectionPanelVisible={inspectionPanelVisible}
      onToggleInspectionPanel={onToggleInspectionPanel}
      navigateTo={(path) => navigate(path)}
      openLink={(url) => window.open(url, "_blank")}
      urls={{ docs: docsUrl }}
    />
  );
};

export default HelpDropdown;
