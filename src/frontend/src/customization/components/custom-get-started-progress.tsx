import { GetStartedProgress } from "@/components/core/folderSidebarComponent/components/sideBarFolderButtons/components/get-started-progress";
import type { Users } from "@/types/api";

export function CustomGetStartedProgress({
  userData,
  handleDismissDialog,
}: {
  userData: Users;
  handleDismissDialog: () => void;
}) {
  return (
    <GetStartedProgress
      userData={userData}
      handleDismissDialog={handleDismissDialog}
    />
  );
}

export default CustomGetStartedProgress;
