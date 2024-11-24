import type { ComponentProps } from 'react';

import { type SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { BetterTooltip } from '@/components/ui/tooltip';

import { SidebarLeftIcon } from './icons';
import { Button } from './ui/button';

export function SidebarToggle({
  className,
}: ComponentProps<typeof SidebarTrigger>) {
  const { toggleSidebar } = useSidebar();

  return (
    <BetterTooltip content="Toggle Sidebar" align="start">
      <Button
        onClick={toggleSidebar}
        variant="outline"
        className="md:px-2 rounded-xl md:h-fit dark:bg-transparent dark:hover:bg-gray-500"
      >
        <SidebarLeftIcon size={16} />
      </Button>
    </BetterTooltip>
  );
}
