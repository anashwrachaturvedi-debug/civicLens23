import React from "react";
import {
  FaGithub,
  FaLinkedin,
  FaXTwitter,
  FaEnvelope,
  FaPhone,
  FaLocationDot,
  FaArrowRight,
} from "react-icons/fa6";

const Footer = () => {
  const quickLinks = [
    { name: "Home", href: "#" },
    { name: "Report Issue", href: "#report" },
    { name: "Dashboard", href: "#dashboard" },
    { name: "Analytics", href: "#analytics" },
  ];

  const socialLinks = [
    {
      icon: <FaGithub size={20} />,
      href: "https://github.com",
      label: "GitHub",
    },
    {
      icon: <FaLinkedin size={20} />,
      href: "https://linkedin.com",
      label: "LinkedIn",
    },
    {
      icon: <FaXTwitter size={20} />,
      href: "https://x.com",
      label: "Twitter",
    },
  ];

  return (
    <footer className="bg-slate-950 text-slate-300 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-5">
              <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-blue-600 text-white font-bold text-lg shadow-lg">
                CL
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">
                  CivicLens AI
                </h2>
                <p className="text-xs text-blue-400 uppercase tracking-widest">
                  Smart City Platform
                </p>
              </div>
            </div>

            <p className="text-slate-400 leading-7">
              Fixing Cities Before Citizens Complain.
            </p>

            <p className="mt-4 text-sm text-slate-500 leading-6">
              AI-powered urban infrastructure monitoring platform that helps
              authorities detect, prioritize, and resolve civic issues faster
              using intelligent analytics.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-5">
              Quick Links
            </h3>

            <ul className="space-y-4">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    className="group flex items-center gap-2 text-slate-400 hover:text-blue-400 transition-all duration-300"
                  >
                    <FaArrowRight className="text-xs group-hover:translate-x-1 transition-transform duration-300" />
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-5">
              Contact
            </h3>

            <div className="space-y-5">
              <div className="flex items-start gap-3">
                <FaEnvelope className="text-blue-400 mt-1" />
                <span className="text-slate-400">
                  contact@civiclens.ai
                </span>
              </div>

              <div className="flex items-start gap-3">
                <FaPhone className="text-blue-400 mt-1" />
                <span className="text-slate-400">
                  +91 98765 43210
                </span>
              </div>

              <div className="flex items-start gap-3">
                <FaLocationDot className="text-blue-400 mt-1" />
                <span className="text-slate-400">
                  India
                </span>
              </div>
            </div>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-5">
              Connect
            </h3>

            <p className="text-slate-400 text-sm leading-6 mb-6">
              Follow CivicLens AI for updates, open-source contributions, and
              smart city innovations.
            </p>

            <div className="flex items-center gap-4">
              {socialLinks.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={item.label}
                  className="w-11 h-11 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:bg-blue-600 hover:text-white hover:-translate-y-1 transition-all duration-300"
                >
                  {item.icon}
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-6 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500 text-center md:text-left">
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-slate-300">
              CivicLens AI
            </span>
            . All rights reserved.
          </p>

          <p className="text-sm text-slate-500 text-center">
            Built with{" "}
            <span className="font-medium text-blue-400">
              React
            </span>{" "}
            &{" "}
            <span className="font-medium text-cyan-400">
              Tailwind CSS
            </span>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;