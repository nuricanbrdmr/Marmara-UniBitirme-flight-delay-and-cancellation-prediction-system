import { Tabs } from "antd";
import { IoAirplane } from "react-icons/io5";
import TravelContent from "./TravelContent";

const Travel = () => {
  return (
    <Tabs
      type="card"
      className="custom-tabs w-[85%] sm:w-[85%] md:w-[85%] lg:w-[60%]"
      items={new Array(1).fill(null).map((_, i) => {
        const id = String(i + 1);
        return {
          label: (
            <span className="flex items-center m-0">
              <IoAirplane size={20} className="mr-2" />
              Flights
            </span>
          ),
          key: id,
          children: <TravelContent />,
        };
      })}
    />
  );
};

export default Travel;
