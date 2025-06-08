import { Carousel } from 'antd';
import heroImg1 from "../assets/images/hero-image_1.webp";
import heroImg2 from "../assets/images/hero-image_2.webp";
import heroImg3 from "../assets/images/hero-image_3.webp";

const imgs = [
    {
        url: heroImg1,
        alt: "hero img 1"
    },
    {
        url: heroImg2,
        alt: "hero img 2"
    },
    {
        url: heroImg3,
        alt: "hero img 3"
    },
];

const Hero = () => {
    return (
        <div className='relative w-full'>
            {/* Overlay text */}
            <div className='absolute w-full top-1/4 left-1/2  transform -translate-x-1/2 flex items-center justify-center z-10'>
                <span className='text-white text-5xl font-bold rounded' style={{ textShadow: '2px 2px 4px rgba(0, 0, 0, 0.7)' }}>
                    Discover the real value of travel
                </span>

            </div>
            {/* Carousel */}
            <Carousel autoplay infinite>
                {imgs.map((img, index) => (
                    <div key={index} className='h-[600px] w-full relative'>
                        <img
                            src={img.url}
                            alt={img.alt}
                            className='h-[90%] w-full object-cover'
                            style={{ borderBottomLeftRadius: '20%', borderBottomRightRadius: '20%' }}
                        />
                    </div>
                ))}
            </Carousel>
        </div>
    );
};

export default Hero;
