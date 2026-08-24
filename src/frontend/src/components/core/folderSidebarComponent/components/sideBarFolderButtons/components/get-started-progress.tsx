import { type FC, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import IconComponent from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import { useGetUserData, useUpdateUser } from "@/controllers/API/queries/auth";
import ModalsComponent from "@/pages/MainPage/components/modalsComponent";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useUtilityStore } from "@/stores/utilityStore";
import type { Users } from "@/types/api";
import { cn } from "@/utils/utils";

export const GetStartedProgress: FC<{
  userData: Users;
  handleDismissDialog: () => void;
}> = ({ userData, handleDismissDialog }) => {
  const { t } = useTranslation();
  const [newProjectModal, setNewProjectModal] = useState(false);
  const hideNewFlowButton = useUtilityStore((state) => state.hideNewFlowButton);

  const flows = useFlowsManagerStore((state) => state.flows);

  const { mutate: mutateLoggedUser } = useGetUserData();
  const { mutate: updateUser } = useUpdateUser();

  useEffect(() => {
    if (!userData) {
      mutateLoggedUser(null);
    }
  }, [userData, mutateLoggedUser]);

  const hasFlows = flows && flows?.length > 0;

  const percentageGetStarted = useMemo(() => (hasFlows ? 100 : 0), [hasFlows]);

  const handleUserTrack = (key: string) => {
    const optins = userData?.optins ?? {};
    optins[key] = true;

    updateUser(
      {
        user_id: userData?.id!,
        user: { optins },
      },
      {
        onSuccess: () => {
          mutateLoggedUser({});
          if (key === "dialog_dismissed") {
            handleDismissDialog();
          }
        },
      },
    );
  };

  return (
    <div className="mt-3 w-full">
      <div className="mb-2 flex items-center justify-between">
        <span
          className="text-sm font-medium"
          data-testid="get_started_progress_title"
        >
          {percentageGetStarted >= 100 ? (
            <>
              <span>{t("sidebar.allSet")}</span>{" "}
              <span className="pl-1"> 🎉 </span>
            </>
          ) : (
            t("sidebar.getStarted")
          )}
        </span>
        <button
          onClick={() => handleUserTrack("dialog_dismissed")}
          className="text-muted-foreground hover:text-foreground"
          data-testid="close_get_started_dialog"
        >
          <IconComponent name="X" className="h-4 w-4" />
        </button>
      </div>

      <div className="mb-1 mt-2 flex items-center justify-between gap-3">
        <div className="h-1 w-full rounded-full bg-muted">
          <div
            className="h-1 rounded-full bg-accent-pink-foreground"
            style={{ width: `${percentageGetStarted}%` }}
          />
        </div>
        <span
          className="text-sm text-muted-foreground"
          data-testid="get_started_progress_percentage"
        >
          {percentageGetStarted}%
        </span>
      </div>

      <div className="mt-2 space-y-1">
        {!hideNewFlowButton && (
          <Button
            unstyled
            className={cn("w-full", hasFlows && "pointer-events-none")}
            onClick={() => setNewProjectModal(true)}
          >
            <div
              className={cn(
                "flex min-w-0 items-center gap-2 rounded-md p-2 py-[10px] hover:bg-muted",
                hasFlows && "pointer-events-none text-muted-foreground",
              )}
              data-testid="create_flow_btn_get_started"
            >
              <span data-testid="create_flow_icon_get_started">
                <IconComponent
                  name={hasFlows ? "Check" : "Plus"}
                  className={cn(
                    "h-4 w-4 shrink-0 text-primary",
                    hasFlows && "text-accent-emerald-foreground",
                  )}
                />
              </span>
              <ShadTooltip content={t("sidebar.createFlow")} side="right">
                <span
                  className={cn("truncate text-sm", hasFlows && "line-through")}
                >
                  {t("sidebar.createFlow")}
                </span>
              </ShadTooltip>
            </div>
          </Button>
        )}
      </div>

      <ModalsComponent
        openModal={newProjectModal}
        setOpenModal={setNewProjectModal}
        openDeleteFolderModal={false}
        setOpenDeleteFolderModal={() => {}}
        handleDeleteFolder={() => {}}
      />
    </div>
  );
};
