import { useState } from "react";
import TravelSearch from "./TravelSearch";

const TravelContent = () => {
    const [selectType, setSelectType] = useState(1);
    const FlightType = [
        {
            id: 1,
            title: "One-Way"
        },
        {
            id: 2,
            title: "Round-Way"
        }
    ];

    return (
        <div className='bg-white w-full h-auto py-3 px-4 rounded-b-xl shadow-lg'>
            <div className="flex items-center gap-3">
                {FlightType.map((type) => (
                    <div
                        key={type.id}
                        onClick={() => setSelectType(type.id)}
                        className={`cursor-pointer text-opacity-80 p-2 rounded-full font-medium ${selectType === type.id
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-200 bg-opacity-60 text-gray-900'
                            }`}
                    >
                        {type.title}
                    </div>
                ))}
            </div>

            <TravelSearch selectType={selectType} />

        </div>
    );
};

export default TravelContent;
