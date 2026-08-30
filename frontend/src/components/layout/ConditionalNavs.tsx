"use client";
import { usePathname } from "next/navigation";
import { TopNav } from "./TopNav";
import { MobileNav } from "./MobileNav";

const HIDE_NAV_ROUTES = ["/chat"];

export function ConditionalNavs() {
  const pathname = usePathname();
  const hideNav = HIDE_NAV_ROUTES.some((route) => pathname.startsWith(route));

  if (hideNav) return null;

  return (
    <>
      <TopNav />
      <MobileNav />
    </>
  );
}
