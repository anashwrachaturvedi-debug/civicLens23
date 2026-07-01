import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function Home() {
    return (
        <>
            <Navbar />

            <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-black text-white">
                <div
                    className="min-h-screen flex items-center justify-center bg-slate-900 text-white text-5xl font-bold"
                >
                    HOME WORKS 🚀
                </div>
                {/* Hero */}
                <section className="max-w-7xl mx-auto px-6 py-24 text-center">
                    <h1 className="text-6xl font-extrabold leading-tight">
                        Fixing cities before
                        <span className="text-cyan-400"> citizens complain.</span>
                    </h1>

                    <p className="mt-8 text-xl text-slate-300 max-w-3xl mx-auto">
                        CivicLens AI detects potholes, garbage, flooding and other urban
                        infrastructure problems using AI and instantly alerts authorities.
                    </p>

                    <div className="mt-10 flex flex-wrap justify-center gap-4">

                        <Link
                            to="/report"
                            className="px-8 py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 transition font-semibold"
                        >
                            Report an Issue
                        </Link>

                        <Link
                            to="/dashboard"
                            className="px-8 py-4 rounded-xl border border-cyan-500 hover:bg-cyan-500/20 transition"
                        >
                            Live Dashboard
                        </Link>

                    </div>
                </section>

                {/* Features */}
                <section className="max-w-7xl mx-auto px-6 py-20">

                    <h2 className="text-4xl font-bold text-center mb-14">
                        Everything authorities need
                    </h2>

                    <div className="grid md:grid-cols-3 gap-8">

                        <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
                            <h3 className="text-2xl font-bold mb-4">
                                AI Detection
                            </h3>

                            <p className="text-slate-300">
                                Detect potholes, garbage, broken street lights and flooding
                                automatically using YOLOv8.
                            </p>
                        </div>

                        <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
                            <h3 className="text-2xl font-bold mb-4">
                                Severity Scoring
                            </h3>

                            <p className="text-slate-300">
                                Every issue receives a priority score so authorities know what
                                to solve first.
                            </p>
                        </div>

                        <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
                            <h3 className="text-2xl font-bold mb-4">
                                Live City Map
                            </h3>

                            <p className="text-slate-300">
                                GPS-tagged issues appear instantly on a real-time interactive
                                map.
                            </p>
                        </div>

                    </div>

                </section>

                {/* CTA */}
                <section className="py-24 text-center">

                    <h2 className="text-5xl font-bold">
                        Ready to improve your city?
                    </h2>

                    <p className="mt-6 text-slate-300 text-lg">
                        Join thousands of citizens making cities smarter.
                    </p>

                    <Link
                        to="/report"
                        className="inline-block mt-10 px-10 py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 transition font-semibold"
                    >
                        Get Started
                    </Link>

                </section>

            </main>

            <Footer />
        </>
    );
}

export default Home;