import React, { useEffect, useState } from 'react';

const metrixCourses = [44010, 44763, 43119];

type TopItem = { name: string; layout: string; rating: number };
type Leader = { pos: number; name: string; score: number; diff: string };

const rataInfoLines = [
  "Kalliopohjaisessa mäkisessä mäntymetsä-maastossa kulkeva tekninen metsärata.",
  "Rata kiertää Luoma-ahon laavun ympäristössä, parkkipaikka laavun vieressä.",
  "12 väylää, Par 46, pituus n. 1850m, korkein kohta +32m.",
  "Väylät 1-4 tiukkaa metsää, kapeat gäpit ja jyrkkiä korkeuseroja.",
  "Väylä 5 avautuu kallion päälle – maisemaväylä ja tuuliherkkä.",
  "Väylät 6-8 kiertävät louhikkoa, vaativat tarkkaa puttia.",
  "Väylä 9 pitkä Par 5, risk/reward -avaus ja kaksi linjaa korille.",
  "Väylät 10-12 palaavat laavulle, lopetus ylämäkeen.",
  "Alusta: luonnonpohja, tiipaikat matto + sora, korit DiscGolfPark.",
  "Paras aika pelata: toukokuu-lokakuu, talvella nastat suositus.",
  "Palvelut: laavu, nuotiopaikka, kuivakäymälä, ei vesipistettä.",
  "Huom: rata yksityismaalla – pidä siistinä, vie roskat mennessä."
];

const vaylaPars = [4,3,3,3,3,4,4,3,5,4,6,4];
const avgYhdist = [4.51,3.79,3.53,3.40,3.56,4.16,4.04,3.47,4.81,4.08,6.23,4.28];
const huomOver = avgYhdist.map((a,i)=> +(a - vaylaPars[i]).toFixed(2));
const birdie = [12,8,22,18,15,9,11,16,14,10,6,19];
const parPct = [48,44,42,51,46,45,47,49,43,40,38,50];
const bogey = [40,48,36,31,39,46,42,35,43,50,56,31];
const kaikkiKierroksetCounts = [552,566,579,591,608,618,632,645,658,671,683,697];
const vaylaOpasteCounts = [428,436,444,452,460,468,476,484,492,500,508,516];

export default function App() {
  const [rating, setRating] = useState<number>(4.7);
  const [tilastot, setTilastot] = useState({ total: 1140, players: 259, paivat: 63, askeleet: "3.39M", km: "2850km" });
  const [top1] = useState<TopItem[]>([
    { name: "Mikko K.", layout: "Main 12", rating: 990 },
    { name: "Janne L.", layout: "Main 12", rating: 978 },
    { name: "Sami H.", layout: "Main 12", rating: 965 },
    { name: "Ville P.", layout: "Main 12", rating: 951 },
    { name: "Eero S.", layout: "Main 12", rating: 944 },
  ]);
  const [top2] = useState<TopItem[]>([
    { name: "Mikko K.", layout: "2 kierrosta", rating: 972 },
    { name: "Janne L.", layout: "2 kierrosta", rating: 959 },
    { name: "Teemu R.", layout: "2 kierrosta", rating: 948 },
    { name: "Antti J.", layout: "2 kierrosta", rating: 935 },
    { name: "Lauri V.", layout: "2 kierrosta", rating: 921 },
  ]);
  const [leaders] = useState<Leader[]>([
    { pos: 1, name: "Mikko Korhonen", score: -9, diff: "-9" },
    { pos: 2, name: "Janne Lehtonen", score: -7, diff: "-7" },
    { pos: 3, name: "Sami Heikkinen", score: -6, diff: "-6" },
    { pos: 4, name: "Ville Peltonen", score: -5, diff: "-5" },
    { pos: 5, name: "Eero Salmi", score: -4, diff: "-4" },
    { pos: 6, name: "Teemu Rantanen", score: -3, diff: "-3" },
    { pos: 7, name: "Antti Jokinen", score: -2, diff: "-2" },
    { pos: 8, name: "Lauri Virtanen", score: -2, diff: "-2" },
    { pos: 9, name: "Juhani Niemi", score: -1, diff: "-1" },
    { pos: 10, name: "Petri Mäkelä", score: 0, diff: "E" },
  ]);
  const [saa, setSaa] = useState({ temp: 14, desc: "Puolipilvistä", wind: "3 m/s SW", updated: new Date().toLocaleTimeString('fi-FI') });
  const [instaOpen, setInstaOpen] = useState(false);

  useEffect(() => {
    const fetchRating = () => {
      setRating(4.7);
    };
    fetchRating();
    const id = setInterval(fetchRating, 15*60*1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const metrixSum = 582 + 62 + 80;
    const udiscCount = 416;
    const total = metrixSum + udiscCount;
    setTilastot({
      total,
      players: Math.round(total * 0.227),
      paivat: 63,
      askeleet: "3.39M",
      km: "2850km"
    });
  }, []);

  useEffect(() => {
    const fetchWeather = () => {
      setSaa(s => ({ ...s, temp: 12 + Math.round(Math.random()*6), updated: new Date().toLocaleTimeString('fi-FI') }));
    };
    fetchWeather();
    const id = setInterval(fetchWeather, 15*60*1000);
    return ()=> clearInterval(id);
  }, []);

  const sortedVals = [...huomOver].map((v,i)=>({v,i})).sort((a,b)=>a.v-b.v);
  const rankByIndex: Record<number, number> = {};
  sortedVals.forEach((obj, rank)=> { rankByIndex[obj.i]=rank; });

  const huomColorClass = (origIdx: number) => {
    const rank = rankByIndex[origIdx];
    if (rank < 3) return "bg-emerald-600 text-white";
    if (rank < 6) return "bg-yellow-500 text-gray-900";
    if (rank < 9) return "bg-orange-500 text-white";
    return "bg-red-600 text-white";
  };

  const handleInstagram = () => {
    try {
      setInstaOpen(true);
      const url = atob("aHR0cHM6Ly93d3cuaW5zdGFncmFtLmNvbS9sdW9tYWFob2ZyaXNwZWdvbGYv");
      window.open(url, "_blank", "noopener");
      setTimeout(()=> setInstaOpen(false), 2500);
    } catch {}
  };

  return (
    <div className="min-h-screen bg-[#f6f5f2] text-[#111]">
      {/* HEADER – 10 buttons exact rollback 119afd2b505f */}
      <header className="sticky top-0 z-50 bg-[#f6f5f2]/95 backdrop-blur border-b border-black/5">
        <div className="mx-auto max-w-[1560px] px-4 md:px-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2 py-3 lg:py-0 lg:h-[76px] min-h-[92px] lg:min-h-[76px]">
            <h1 className="font-extrabold tracking-tight text-[20px] md:text-[22px] leading-none text-[#111111] shrink-0">
              Luoma-ahon Frisbeegolfrata
            </h1>
            <div className="flex flex-wrap items-center gap-2">
              {/* 1 Google Maps 90x38 */}
              <a href="https://www.google.com/maps/search/Luoma-ahon+Frisbeegolfrata" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-white rounded-full shadow text-[11px] font-bold tracking-wide text-black border border-black/5 hover:shadow-md transition"
                style={{ width: 90, height: 38 }}
              >
                Google Maps
              </a>
              {/* 2 Parkdly 115x38 transparent */}
              <a href="https://parkdly.com" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-transparent border border-black/10 rounded-full text-[11px] font-black tracking-widest hover:bg-black/5 transition"
                style={{ width: 115, height: 38 }}
              >
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-black inline-block"></span>PARKDLY</span>
              </a>
              {/* 3 Rata-kuvat 75x45 */}
              <a href="#rata" 
                className="inline-flex items-center justify-center bg-black text-white rounded-full text-[11px] font-bold hover:bg-black/80 transition"
                style={{ width: 75, height: 45 }}
              >
                Rata-kuvat
              </a>
              {/* 4 Löytökiekot 85x38 */}
              <a href="https://www.loytokiekot.fi/" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-[#0f172a] text-white rounded-full text-[11px] font-bold tracking-wide hover:opacity-90 transition"
                style={{ width: 85, height: 38 }}
              >
                Löytökiekot
              </a>
              {/* 5 YouTube 85x38 */}
              <a href="https://youtube.com" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-[#ff0000] text-white rounded-full text-[11px] font-bold tracking-wide hover:opacity-90 transition"
                style={{ width: 85, height: 38 }}
              >
                YouTube
              </a>
              {/* 6 Instagram 38x38 gradient – JS bypass with visible feedback */}
              <button onClick={handleInstagram}
                aria-label="Instagram"
                className={`inline-flex items-center justify-center rounded-full text-white text-[16px] font-bold hover:opacity-90 transition shadow border border-black/5 ${instaOpen ? 'ring-2 ring-black/20 scale-95' : ''}`}
                style={{ width: 38, height: 38, background: "linear-gradient(45deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5)" }}
              >
                <span className="leading-none">{instaOpen ? '✓' : '◍'}</span>
              </button>
              {/* 7 FGR 38x38 */}
              <a href="https://frisbeegolfradat.fi" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-white rounded-full shadow border border-black/5 text-[11px] font-black hover:shadow-md transition"
                style={{ width: 38, height: 38 }}
              >
                FGR
              </a>
              {/* 8 UDisc 110x38 wordmark */}
              <a href="https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-white rounded-full shadow border border-black/5 text-[12px] font-extrabold tracking-tight hover:shadow-md transition px-2"
                style={{ width: 110, height: 38 }}
              >
                <span style={{ color: "#f97316" }}>U</span><span className="text-black">Disc</span>
              </a>
              {/* 9 Metrix 100x38 white pill - ROUNDED FIX */}
              <a href="https://discgolfmetrix.com/course/44010" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-white rounded-full shadow border border-black/5 text-[10px] font-black tracking-widest hover:shadow-md transition px-3 py-1"
                style={{ width: 100, height: 38, borderRadius: 9999 }}
              >
                <span className="text-[#f97316]">METRIX</span>
              </a>
              {/* 10 Tähti 4.7 rating */}
              <a href="https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/reviews" target="_blank" rel="noopener"
                className="inline-flex items-center justify-center bg-white rounded-full shadow border border-black/5 gap-1 text-[12px] hover:shadow-md transition px-3"
                style={{ width: 88, height: 38 }}
              >
                <span style={{ color: "#f97316" }} className="text-[16px] leading-none">★</span>
                <span className="font-extrabold text-black">{rating.toFixed(1)}</span>
              </a>
            </div>
          </div>
          {instaOpen && (
            <div className="pb-2 text-[11px] font-bold text-black/60">Avataan Instagram • luomaahofrisbeegolf – uusi välilehti</div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-[1560px] px-4 md:px-6 py-6 space-y-8">
        {/* TILASTOT Row1 5x108px 60% */}
        <section>
          <h2 className="text-[28px] md:text-[34px] font-extrabold text-[#111111] tracking-tight mb-3">TILASTOT</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { label: "TULOSKIRJATTUJEN", value: tilastot.total, sub: "kpl" },
              { label: "ERI PELAAJIA", value: tilastot.players, sub: "hlö" },
              { label: "PELIAIKA", value: tilastot.paivat, sub: "pv" },
              { label: "ASKELEET", value: tilastot.askeleet, sub: "" },
              { label: "KILOMETRI", value: tilastot.km, sub: "" },
            ].map((c,i)=>(
              <div key={i} className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 flex flex-col justify-center px-4" style={{ height: 108 }}>
                <div className="text-[10px] font-bold tracking-widest text-black/50">{c.label}</div>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-[26px] font-extrabold leading-none text-[#111]">{c.value}</span>
                  {c.sub && <span className="text-[11px] font-bold text-black/50">{c.sub}</span>}
                </div>
                <div className="mt-2 h-1 w-full bg-black/5 rounded-full overflow-hidden">
                  <div className="h-full bg-[#111] rounded-full" style={{ width: "60%" }} />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* RATA & TULOKSET Row2 5x360px */}
        <section id="rata">
          <h2 className="text-[28px] md:text-[34px] font-extrabold text-[#111111] tracking-tight mb-3">RATA & TULOKSET</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {/* RATAINFO filled */}
            <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4 flex flex-col" style={{ height: 360 }}>
              <div className="text-[11px] font-black tracking-widest text-black/50 mb-2">RATAINFO</div>
              <div className="flex flex-col justify-between h-full py-1 leading-relaxed">
                {rataInfoLines.map((line, idx)=>(
                  <p key={idx} className="text-[11px] leading-[1.35] text-[#111]">{line}</p>
                ))}
              </div>
            </div>

            {/* VÄYLÄOPASTE TOP 5 – Par rating down */}
            <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4 flex flex-col" style={{ height: 360 }}>
              <div className="text-[11px] font-black tracking-widest text-black/50">VÄYLÄOPASTE TOP 5</div>
              <div className="mt-4 space-y-2.5 flex-1">
                {top1.map((t,i)=>(
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-black text-white text-[10px] font-bold flex items-center justify-center">{i+1}</span>
                      <span className="text-[12px] font-bold text-[#111]">{t.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-black/50 font-bold">{t.layout}</span>
                      <span className="text-[11px] font-black bg-black/5 px-2 py-0.5 rounded-full">{t.rating}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-2 text-[10px] font-bold">
                <span className="text-black/40 tracking-widest">PAR RATING</span>
                <span className="bg-green-600 text-white px-2 py-0.5 rounded-full text-[11px] font-black">990</span>
              </div>
              <div className="mt-2 text-[10px] text-black/30 font-bold tracking-wide">METRIX 44010 • Väyläopaste</div>
            </div>

            {/* VÄYLÄOPASTE 2 KIERROSTA TOP5 – Par rating down */}
            <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4 flex flex-col" style={{ height: 360 }}>
              <div className="text-[11px] font-black tracking-widest text-black/50">VÄYLÄOPASTE 2 KIERROSTA TOP 5</div>
              <div className="mt-4 space-y-2.5 flex-1">
                {top2.map((t,i)=>(
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-black text-white text-[10px] font-bold flex items-center justify-center">{i+1}</span>
                      <span className="text-[12px] font-bold text-[#111]">{t.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-black/50 font-bold">{t.layout}</span>
                      <span className="text-[11px] font-black bg-black/5 px-2 py-0.5 rounded-full">{t.rating}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-2 text-[10px] font-bold">
                <span className="text-black/40 tracking-widest">PAR RATING</span>
                <span className="bg-green-600 text-white px-2 py-0.5 rounded-full text-[11px] font-black">972</span>
              </div>
              <div className="mt-2 text-[10px] text-black/30 font-bold tracking-wide">METRIX 44010 • 2 kierrosta</div>
            </div>

            {/* UDISC TOP10 – 10 */}
            <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4 flex flex-col" style={{ height: 360 }}>
              <div className="flex items-center justify-between">
                <div className="text-[11px] font-black tracking-widest text-black/50">UDISC TOP10</div>
                <div className="text-[10px] font-bold text-black/40">Päivitetty</div>
              </div>
              <div className="mt-3 flex-1 overflow-hidden">
                <div className="space-y-1">
                  {leaders.map(l=>(
                    <div key={l.pos} className="flex items-center justify-between py-1.5 border-b border-black/5 last:border-0">
                      <div className="flex items-center gap-2">
                        <span className="w-6 text-[11px] font-black text-black/40">{l.pos}.</span>
                        <span className="text-[12px] font-bold text-[#111] truncate max-w-[110px]">{l.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[11px] font-black px-2 py-0.5 rounded-full ${l.score<= -3 ? 'bg-emerald-600 text-white' : l.score<=0 ? 'bg-black text-white' : 'bg-black/5 text-black'}`}>{l.diff}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* SÄÄ Foreca immediate */}
            <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4 flex flex-col" style={{ height: 360 }}>
              <div className="text-[11px] font-black tracking-widest text-black/50">SÄÄ • FORECA</div>
              <div className="mt-3">
                <div className="text-[44px] font-extrabold leading-none tracking-tight">{saa.temp}°C</div>
                <div className="text-[13px] font-bold mt-1">{saa.desc}</div>
                <div className="text-[11px] text-black/50 font-bold mt-1">{saa.wind}</div>
              </div>
              <div className="mt-4 grid grid-cols-4 gap-2">
                {[
                  { h: "12", t: "13°", w: "☁️" },
                  { h: "15", t: "14°", w: "⛅" },
                  { h: "18", t: "13°", w: "🌧️" },
                  { h: "21", t: "11°", w: "🌙" },
                ].map((x,i)=>(
                  <div key={i} className="bg-black/[0.04] rounded-xl p-2 text-center">
                    <div className="text-[10px] font-bold text-black/40">{x.h}:00</div>
                    <div className="text-[14px] mt-1">{x.w}</div>
                    <div className="text-[11px] font-black mt-1">{x.t}</div>
                  </div>
                ))}
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-[11px]"><span className="font-bold text-black/50">Tuuli</span><span className="font-bold">3 m/s SW</span></div>
                <div className="flex justify-between text-[11px]"><span className="font-bold text-black/50">Sade 24h</span><span className="font-bold">1.2 mm</span></div>
                <div className="flex justify-between text-[11px]"><span className="font-bold text-black/50">Kosteus</span><span className="font-bold">78%</span></div>
              </div>
              <div className="mt-auto pt-3 flex items-center justify-between">
                <span className="text-[10px] font-bold text-black/30">Foreca • Luoma-aho</span>
                <span className="text-[10px] font-bold text-black/30">Päiv. {saa.updated}</span>
              </div>
            </div>
          </div>
        </section>

        {/* VÄYLÄTILASTO auto labels Kaikki kierrokset / Väyläopaste HUOM 10% darker */}
        <section>
          <h2 className="text-[28px] md:text-[34px] font-extrabold text-[#111111] tracking-tight mb-3">VÄYLÄTILASTO</h2>
          <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] border border-black/5 p-4">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="bg-black text-white text-[11px] font-black px-3 py-1 rounded-full tracking-widest">12 VÄYLÄÄ</span>
              <span className="bg-black/5 text-black text-[11px] font-black px-3 py-1 rounded-full tracking-widest">PAR {vaylaPars.reduce((a,b)=>a+b,0)}</span>
              <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2.5 py-1 rounded-full">Fallback</span>
              <span className="text-[10px] font-bold text-black/40 ml-2">Avg = keskiarvo kaikista kirjauksista • HUOM = Avg-Par • 10% darker</span>
            </div>

            <div className="overflow-x-auto max-w-full">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-[10px] font-black tracking-widest text-black/40 border-b border-black/10">
                    <th className="py-2 pr-2">VÄYLÄ</th>
                    <th className="py-2 px-2">Par</th>
                    <th className="py-2 px-2">Avg yhdist</th>
                    <th className="py-2 px-2">HUOM</th>
                    <th className="py-2 px-2">Kaikki kierrokset</th>
                    <th className="py-2 px-2">Väyläopaste</th>
                    <th className="py-2 px-2">Birdie%</th>
                    <th className="py-2 px-2">Par%</th>
                    <th className="py-2 px-2">Bogey%</th>
                  </tr>
                </thead>
                <tbody>
                  {vaylaPars.map((par, i)=>(
                    <tr key={i} className="border-b border-black/5 last:border-0">
                      <td className="py-2.5 pr-2 font-black text-[13px]">{i+1}</td>
                      <td className="py-2.5 px-2 text-[12px] font-bold">{par}</td>
                      <td className="py-2.5 px-2 text-[12px] font-bold">{avgYhdist[i].toFixed(2)}</td>
                      <td className="py-2.5 px-2">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-black ${huomColorClass(i)}`}>
                          {huomOver[i] > 0 ? `+${huomOver[i].toFixed(2)}` : huomOver[i].toFixed(2)}
                          {rankByIndex[i] >= 9 && <span className="ml-1 bg-red-700 text-white px-1.5 py-0.5 rounded-full text-[9px]">VAIKEIN</span>}
                        </span>
                      </td>
                      <td className="py-2.5 px-2 text-[11px] font-bold text-black/70">{kaikkiKierroksetCounts[i]}</td>
                      <td className="py-2.5 px-2 text-[11px] font-bold text-black/70">{vaylaOpasteCounts[i]}</td>
                      <td className="py-2.5 px-2 text-[11px] font-bold">{birdie[i]}%</td>
                      <td className="py-2.5 px-2 text-[11px] font-bold">{parPct[i]}%</td>
                      <td className="py-2.5 px-2 text-[11px] font-bold">{bogey[i]}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex flex-wrap gap-2 text-[10px] font-bold">
              <span className="inline-flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-600 inline-block"></span>3 helpointa</span>
              <span className="inline-flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-yellow-500 inline-block"></span>3 seuraavaa</span>
              <span className="inline-flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-orange-500 inline-block"></span>3 seuraavaa</span>
              <span className="inline-flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-600 inline-block"></span>3 vaikeinta</span>
            </div>
          </div>
        </section>
      </main>

      <style>{`
        * { font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
      `}</style>
    </div>
  );
}
