import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';


export const experimental_ppr = true;

export default function Layout({
                                   children,
                               }: {
    children: React.ReactNode;
}) {
    // Directly use the children without checking for authentication or session
    const isCollapsed = false; // Set default to not collapsed (or whatever you prefer)

    return (
        <SidebarProvider defaultOpen={!isCollapsed}>
            <AppSidebar  user={undefined}/> {/* No user session, so pass null */}
            <SidebarInset>{children}</SidebarInset>
        </SidebarProvider>
    );
}