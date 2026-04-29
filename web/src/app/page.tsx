import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Downloads from "@/components/Downloads";
import HowItWorks from "@/components/HowItWorks";
import GettingStarted from "@/components/GettingStarted";
import SearchSyntax from "@/components/SearchSyntax";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Downloads />
        <SearchSyntax />
        <GettingStarted />
        <FAQ />
      </main>
      <Footer />
    </>
  );
}
