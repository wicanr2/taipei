// #20：原版 OPL 暫存器序列的離線 YM3812 研究原型。
// 外部核心固定版本與授權見 workspace/cache/ymfm-reference/source.json。
#include "ymfm_opl.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>

struct Event { uint64_t step; unsigned bank,reg,value; };
static void u16(std::ostream &o,uint16_t n) { o.put(n&255);o.put(n>>8); }
static void u32(std::ostream &o,uint32_t n) { u16(o,n&65535);u16(o,n>>16); }
int main(int argc,char **argv) {
    if(argc!=5) { std::cerr<<"events.txt output.wav final-steps steps-per-second\n";return 2; }
    std::ifstream in(argv[1]);
    if(!in) throw std::runtime_error("OPL event file missing");
    std::vector<Event> events;
    Event e{};
    while(in>>e.step>>e.bank>>e.reg>>e.value) {
        if(e.bank!=0 || e.reg>255 || e.value>255) throw std::runtime_error("not OPL2 events");
        if(!events.empty() && e.step<events.back().step) throw std::runtime_error("events not ordered");
        events.push_back(e);
    }
    const uint64_t final_steps=std::stoull(argv[3]);
    const double sps=std::stod(argv[4]);
    if(events.empty() || final_steps>2000000000ULL || sps<1000000) throw std::runtime_error("invalid bounded input");
    ymfm::ymfm_interface intf;
    ymfm::ym3812 chip(intf);
    chip.reset();
    const uint32_t rate=chip.sample_rate(3579545);
    const uint32_t frames=uint32_t(std::floor(double(final_steps)/sps*rate));
    std::ofstream out(argv[2],std::ios::binary);
    if(!out) throw std::runtime_error("output failed");
    out.write("RIFF",4);u32(out,36+frames*2);out.write("WAVEfmt ",8);u32(out,16);
    u16(out,1);u16(out,1);u32(out,rate);u32(out,rate*2);u16(out,2);u16(out,16);
    out.write("data",4);u32(out,frames*2);
    size_t next=0;
    uint64_t nonzero=0,clipped=0;
    int peak=0;
    double energy=0;
    for(uint32_t i=0;i<frames;i++) {
        const uint64_t step=uint64_t(double(i)*sps/rate);
        while(next<events.size() && events[next].step<=step) {
            chip.write_address(uint8_t(events[next].reg));chip.write_data(uint8_t(events[next].value));next++;
        }
        ymfm::ym3812::output_data sample;
        chip.generate(&sample);
        const int raw=sample.data[0];
        clipped+=raw>32767 || raw<-32768;
        const int v=std::max(-32768,std::min(32767,raw));
        nonzero+=v!=0;peak=std::max(peak,std::abs(v));energy+=double(v)*v;
        u16(out,uint16_t(int16_t(v)));
    }
    out.close();
    std::cout<<"{\"schema\":1,\"prototype\":true,\"sample_rate\":"<<rate
             <<",\"frames\":"<<frames<<",\"events\":"<<events.size()
             <<",\"consumed_events\":"<<next<<",\"nonzero\":"<<nonzero
             <<",\"peak\":"<<peak<<",\"clipped\":"<<clipped
             <<",\"rms\":"<<std::sqrt(energy/frames)
             <<",\"timing\":\"hardware-spec approximation\"}\n";
}
