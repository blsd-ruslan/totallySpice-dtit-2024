'use client';

import type {User} from 'next-auth';
import {useRouter} from 'next/navigation';

import {PlusIcon} from '@/components/icons';
import {SidebarHistory} from '@/components/sidebar-history';
import {SidebarUserNav} from '@/components/sidebar-user-nav';
import {Button} from '@/components/ui/button';
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarHeader,
    SidebarMenu,
    useSidebar,
} from '@/components/ui/sidebar';
import {BetterTooltip} from '@/components/ui/tooltip';
import Link from 'next/link';
import {useState} from "react";

export function AppSidebar({user}: { user: User | undefined }) {
    const router = useRouter();
    const {setOpenMobile} = useSidebar();
    const [activeTab, setActiveTab] = useState('tab1'); // Set the initial active tab

    return (
        <Sidebar className="group-data-[side=left]:border-r-0">
            <SidebarHeader>
                <SidebarMenu>
                    <div className="flex flex-row justify-between items-center">
                        <Link
                            href="/"
                            onClick={() => {
                                setOpenMobile(false);
                            }}
                            className="flex flex-row gap-3 items-center"
                        >
              <span className="text-lg font-semibold px-2 hover:bg-muted rounded-md cursor-pointer">
                Chatbot
              </span>
                        </Link>
                        <BetterTooltip content="New Chat" align="start">
                            <Button
                                variant="ghost"
                                type="button"
                                className="p-2 h-fit"
                                onClick={() => {
                                    setOpenMobile(false);
                                    router.push('/');
                                    router.refresh();
                                }}
                            >
                                <PlusIcon/>
                            </Button>
                        </BetterTooltip>
                    </div>
                </SidebarMenu>
            </SidebarHeader>

            <SidebarContent>
                <SidebarGroup>
                    <div className="flex flex-col gap-4 mt-4">
                        <div
                            className={`cursor-pointer px-4 py-2 rounded-md ${
                                activeTab === 'tab1' ? 'bg-[#E20074] text-white drop-shadow-glow' : 'hover:bg-muted'
                            }`}
                            onClick={() => setActiveTab('tab1')}
                        >
                            Finance document
                        </div>
                        <div
                            className={`cursor-pointer px-4 py-2 rounded-md ${
                                activeTab === 'tab2' ? 'bg-[#E20074] text-white drop-shadow-glow' : 'hover:bg-muted'
                            }`}
                            onClick={() => setActiveTab('tab2')}
                        >
                            Building permit
                        </div>
                        <div
                            className={`cursor-pointer px-4 py-2 rounded-md ${
                                activeTab === 'tab3' ? 'bg-[#E20074] text-white drop-shadow-glow' : 'hover:bg-muted'
                            }`}
                            onClick={() => setActiveTab('tab3')}
                        >
                            Residence permit
                        </div>
                    </div>

                    {/* Sidebar History */}
                    {/*<SidebarHistory user={user}/>*/}
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="gap-0 -mx-2">
                {user && (
                    <SidebarGroup>
                        <SidebarGroupContent>
                            <SidebarUserNav user={user}/>
                        </SidebarGroupContent>
                    </SidebarGroup>
                )}
            </SidebarFooter>
        </Sidebar>
    );
}