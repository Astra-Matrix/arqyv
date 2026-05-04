import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import Marquee from "@/components/Marquee";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import TerminalShowcase from "@/components/TerminalShowcase";
import Downloads from "@/components/Downloads";
import SearchSyntax from "@/components/SearchSyntax";
import GettingStarted from "@/components/GettingStarted";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Marquee />
        <Features />
        <HowItWorks />
        <TerminalShowcase />
        <Downloads />
        <SearchSyntax />
        <GettingStarted />
        <FAQ />
      </main>
      <Footer />
    </>
  );
}
