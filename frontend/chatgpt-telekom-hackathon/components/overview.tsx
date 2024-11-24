import { motion } from 'framer-motion';

import { MagentaLogo } from './icons';
import PDFViewer from "@/components/pdf-viewer";

export const Overview = () => {
  const testPdf = "/documents/ew.pdf";
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-7xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <MagentaLogo size={48} />
        </p>
        <p className="dark:text-white">Ask help about documents</p>
      </div>
    </motion.div>
  );
};
