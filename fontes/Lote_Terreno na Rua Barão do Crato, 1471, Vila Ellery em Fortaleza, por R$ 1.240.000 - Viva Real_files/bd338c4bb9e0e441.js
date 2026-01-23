(globalThis.TURBOPACK||(globalThis.TURBOPACK=[])).push(["object"==typeof document?document.currentScript:void 0,75475,e=>{"use strict";var a=e.i(843476),i=e.i(271645),t=e.i(651774),n=e.i(309700);e.i(310669);var s=e.i(281189);e.i(595910);var r=e.i(123381);e.i(894307);var c=e.i(952277),l=e.i(598602);e.i(451321);var o=e.i(326545),m=e.i(897564);function d(){let{page:{account:e,listingId:d,prices:u,address:x}}=(0,o.usePageData)(),[f,h]=(0,i.useState)("");(0,i.useEffect)(()=>{p()},[]);let p=async()=>{h(await (0,m.getPartner)({price:u[0].price||"0",accountId:e.id,listingId:d,addressState:x.stateAcronym}))};return(0,a.jsx)(r.default,{className:"mt-2 max-[1024px]:mt-3",children:(0,a.jsxs)(s.default,{spacing:"medium",children:[(0,a.jsx)("h2",{className:"text-2-5 text-neutral-120 font-semibold max-[1024px]:text-2-25",children:"Precisa financiar?"}),(0,a.jsxs)("div",{className:"financing-stack",children:[(0,a.jsx)("div",{className:"financing-stack_text",children:(0,a.jsxs)("p",{className:"text-1-75 text-neutral-120 font-secondary",children:["O ",c.default.name," te ajuda! Simule agora seu financiamento, e se gostar, envie uma proposta ",(0,a.jsx)("strong",{children:"em menos de 5 minutos"}),"."]})}),(0,a.jsx)("a",{href:f,target:"_blank",rel:"noreferrer",children:(0,a.jsxs)(t.Button,{className:`
                h-auto
                min-[1024px]:w-[225px]
                max-[1024px]:w-full
                whitespace-normal
                flex
                justify-center
                items-center
                shadow-none
                bg-primary-70
              `,variant:"tertiary",size:"small",onClick:()=>{l.track.financialSimulatorClicked({action:"REDIRECT",screen:"TOP_BUTTON",listing:{id:d},targetUrl:f})},children:[(0,a.jsx)(n.DollarSignCircle,{size:16}),"Simular financiamento"]})})]})]})})}e.s([],288870),e.i(288870),e.s(["default",()=>d],75475)},413099,e=>{e.n(e.i(75475))}]);