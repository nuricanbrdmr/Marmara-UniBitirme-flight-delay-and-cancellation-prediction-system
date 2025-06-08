import { Tag, Tooltip, Progress } from "antd";
import { AiOutlineClockCircle, AiOutlineRobot } from "react-icons/ai";
import { MdFlightTakeoff, MdFlightLand } from "react-icons/md";
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BsStars } from "react-icons/bs";

const Ticket = ({
  logo,
  airline,
  departureTime,
  duration,
  arrivalTime,
  departureCode,
  arrivalCode,
  price,
  model
}) => {
  const [isCollapseOpen, setIsCollapseOpen] = useState(false);

  const getDelayColor = (delayClass) => {
    switch (delayClass) {
      case "Zamanında veya erken":
        return "green";
      case "Hafif gecikme (1-15 dakika)":
        return "processing";
      case "Orta gecikme (16-30 dakika)":
        return "warning";
      case "Ciddi gecikme (30+ dakika)":
        return "error";
      default:
        return "default";
    }
  };

  const getDelayIcon = (delayClass) => {
    switch (delayClass) {
      case "Zamanında veya erken":
        return <MdFlightTakeoff />;
      case "Hafif gecikme (1-15 dakika)":
        return <AiOutlineClockCircle />;
      case "Orta gecikme (16-30 dakika)":
        return <AiOutlineClockCircle />;
      case "Ciddi gecikme (30+ dakika)":
        return <MdFlightLand />;
      default:
        return <AiOutlineClockCircle />;
    }
  };

  return (
    <>
      <div className="flex max-sm:flex-col items-center gap-5 w-[70%] max-sm:w-[98%] mx-auto max-sm:mx-1 mt-6 border rounded-lg py-8 px-5">
        <div className="flex justify-between gap-10 sm:gap-14 w-full">
          <div className="flex items-center max-sm:flex-col max-sm:gap-1 sm:gap-2 md:gap-5 lg:gap-10">
            <img
              src={logo}
              alt={airline}
              className="w-12 h-12 max-sm:w-8 max-sm:h-8 md:w-16 md:h-16 object-contain"
            />
            <span className="text-base md:text-lg font-medium">{airline}</span>
          </div>
          <div className="flex flex-col w-full md:w-1/2">
            <div className="flex items-center justify-between gap-4">
              <span className="text-gray-800 font-semibold">{departureTime}</span>
              <span className="text-gray-500 text-sm hidden md:block">
                {duration}
              </span>
              <span className="text-gray-800 font-semibold">{arrivalTime}</span>
            </div>
            <div className="relative w-full mx-auto flex items-center justify-between">
              <span className="bg-white border-2 z-10 border-gray-300 rounded-full h-3 w-3"></span>
              <span className="absolute left-[10px] z-0 bg-gray-100 w-[98%] h-1 border"></span>
              <span className="bg-white border-2 z-10 border-gray-300 rounded-full h-3 w-3"></span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[16px] text-gray-600 font-semibold">
                {departureCode}
              </span>
              <span className="text-gray-500 text-sm">Direct</span>
              <span className="text-[16px] text-gray-600 font-semibold">
                {arrivalCode}
              </span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 w-full md:w-auto items-center justify-center">
            {model?.data?.predictions?.cancelled ? (
              <Tag
                color="error"
                className="flex items-center gap-2 py-0.5"
              >
                <FaRobot className="text-lg" />
                İptal Riski Yüksek
              </Tag>
            ) : (
              <Tag
                color={getDelayColor(model?.data?.predictions?.delay?.delay_class)}
                className="flex items-center gap-2 py-0.5"
              >
                {getDelayIcon(model?.data?.predictions?.delay?.delay_class)}
                {model?.data?.predictions?.delay?.delay_class}
              </Tag>
            )}
            <Tooltip title="AI Tahmin Güven Oranı">
              <Tag
                color="blue"
                className="flex items-center gap-2 py-0.5"
              >
                <AiOutlineRobot className="text-lg" />
                {Math.round(model?.data?.predictions?.confidence * 100)}% Güven
              </Tag>
            </Tooltip>
            <Tag
              color="cyan"
              className="flex items-center gap-2 py-1 my-2 cursor-pointer hover:opacity-80"
              onClick={() => setIsCollapseOpen(!isCollapseOpen)}
            >
              <BsStars className="text-lg" />
              <span>FCDP-SFTS AI Model Tahmin Detayları</span>
            </Tag>
          </div>
        </div>
        <div className="relative flex flex-col items-center md:border-l-2 md:border-dashed md:pl-6 mt-4 md:mt-0">
          <div className="text-center">
            <h2 className="text-xl md:text-2xl font-bold flex items-baseline gap-1 justify-center">
              {price}
            </h2>
            <span className="text-gray-500 text-sm">Per person</span>
          </div>
        </div>
      </div>
      <div className="w-[70%] max-sm:w-[98%] mx-auto max-sm:mx-1">
        <AnimatePresence>
          {isCollapseOpen && (
            <motion.div
              key="ai-details"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
              style={{ overflow: 'hidden' }}
              className="space-y-4 p-4 bg-gray-50 border border-gray-200 mt-2 rounded-lg"
            >
              <div>
                <h2 className="text-xl text-center font-bold mb-2">
                  <span className="bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 bg-clip-text text-transparent">
                    FCDP-SFTS AI Model Tahmin Detayları
                  </span>
                </h2>
                <h3 className="font-semibold mb-2">İptal Durumu</h3>
                <div className="flex items-center gap-4">
                  <Progress
                    type="circle"
                    percent={Math.round(model?.data?.predictions?.cancelled_probability?.cancelled * 100)}
                    format={(percent) => `${percent}%`}
                    strokeColor="#ff4d4f"
                  />
                  <Progress
                    type="circle"
                    percent={Math.round(model?.data?.predictions?.cancelled_probability?.not_cancelled * 100)}
                    format={(percent) => `${percent}%`}
                    strokeColor="#52c41a"
                  />
                  <div>
                    <p className="text-sm text-gray-600">
                      İptal Olasılığı: <span className="font-bold">{Math.round(model?.data?.predictions?.cancelled_probability?.cancelled * 100)}%</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      İptal Olmama Olasılığı: <span className="font-bold">{Math.round(model?.data?.predictions?.cancelled_probability?.not_cancelled * 100)}%</span>
                    </p>
                  </div>
                </div>
              </div>

              {!model?.data?.predictions?.cancelled && (
                <div>
                  <h3 className="font-semibold mb-2">Gecikme Tahmini</h3>
                  <div className="space-y-2">
                    {Object.entries(model?.data?.predictions?.delay?.delay_probabilities || {}).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <span className="w-48 text-sm text-gray-600">{key}:</span>
                        <Progress
                          percent={Math.round(value * 100)}
                          size="small"
                          status={key === model?.data?.predictions?.delay?.delay_class ? "active" : "normal"}
                          strokeColor={key === "Zamanında veya erken" ? "#52c41a" : "#ff4d4f"}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="font-semibold mb-2">Model Ayarlamaları</h3>
                <div className="flex flex-wrap gap-2">
                  {model?.data?.predictions?.model_adjustments?.corrections_applied.map((correction, index) => (
                    <Tag key={index} color="blue">
                      {correction}
                    </Tag>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
};

export default Ticket;
