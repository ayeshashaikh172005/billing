<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Control Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <!-- Chart.js for data visualization -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Font Awesome for Home Tab icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --navy: #000080;
            --navy-light: #0000CD;
            --builder-blue: #3b82f6;
        }
        .glass-header { background: #000040; border-bottom: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(12px); }
        .cyber-card { background: #ffffff; border: 1px solid #000080; box-shadow: 0 4px 15px rgba(0,0,128,0.05); transition: transform 0.2s ease; }
        .cyber-card:hover { transform: translateY(-2px); }
        .shimmer { 
            background: linear-gradient(90deg, #000080, #0000CD, #3b82f6, #000080); 
            background-size: 200% auto; 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            animation: shimmer 4s linear infinite; 
        }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
        .active-tab { background: rgba(255, 255, 255, 0.15); border-bottom: 3px solid #ffffff; color: #ffffff; }
        
        .banner-gradient { background: linear-gradient(90deg, #e0f2fe 0%, #dbeafe 100%); }

        /* Custom Scrollbar for Navy theme */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f8fafc; }
        ::-webkit-scrollbar-thumb { background: #000080; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #000040; }

        .success-toast {
            animation: slideUp 0.3s ease-out forwards;
        }
        @keyframes slideUp {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .billing-cart-area { max-height: 450px; overflow-y: auto; }
        .chart-container { position: relative; height: 280px; width: 100%; }

        /* Review Slider Animations */
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(calc(-250px * 5)); }
        }
        .slider-track {
            display: flex;
            width: calc(250px * 10);
            animation: scroll 30s linear infinite;
        }
        .slider-track:hover {
            animation-play-state: paused;
        }

         /* Builder Specific Styles */
        .builder-modal {
            transition: all 0.2s ease-out;
            opacity: 0;
            transform: translate(-50%, -45%) scale(0.95);
            pointer-events: none;
        }

        .builder-modal.open {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
            pointer-events: auto;
        }
        .fade-in { animation: fadeIn 0.2s ease-out forwards; }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .builder-scroll::-webkit-scrollbar { width: 6px; }
        .builder-scroll::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
    </style>

</head>
<body class="text-[#000080] min-h-screen font-sans selection:bg-blue-200 bg-[#f9fafb] overflow-x-hidden">

    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // Custom Rupee Coin SVG Component
        const RupeeCoinSVG = ({ className }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
                <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0-18 0"/>
                <path d="M15 8H9h1a3 3 0 0 1 0 6H9l3 3m-3-6h6"/>
            </svg>
        );

        const ReviewSlider = () => {
            const reviews = [
                { name: "Arjun Mehta", role: "CEO, Techflow", text: "The document conversion tool saved us 20 hours a week.", stars: 5 },
                { name: "Justin Martin", role: "Ops Manager", text: "Most stable ERP node we have ever integrated. 10/10.", stars: 5 },
                { name: "Vikram Singh", role: "Retail Owner", text: "Billing is now a breeze. My staff learned it in 5 minutes.", stars: 4 },
                { name: "Hamza Khan", role: "Accountant", text: "The analytics dashboards are incredibly detailed and fast.", stars: 5 },
                { name: "Marcus Thorne", role: "Logistics Lead", text: "E-way bill integration is seamless. Huge fan of the UI.", stars: 5 },
                { name: "Alfiya Shaikh", role: "CEO, Techflow", text: "The document conversion tool saved us 20 hours a week.", stars: 5 },
                { name: "Sarah Jenkins", role: "Ops Manager", text: "Most stable ERP node we have ever integrated. 10/10.", stars: 5 },
                { name: "Ayesha Shaikh", role: "Retail Owner", text: "Billing is now a breeze. My staff learned it in 5 minutes.", stars: 4 },
                { name: "Priya Rao", role: "Accountant", text: "The analytics dashboards are incredibly detailed and fast.", stars: 5 },
                { name: "Jasmine Shaikh", role: "Logistics Lead", text: "E-way bill integration is seamless. Huge fan of the UI.", stars: 5 }
            ];

            const displayReviews = [...reviews, ...reviews];

            return (
                <div className="w-full overflow-hidden py-10">
                    <div className="mb-8 text-left text-navy">
                        <h3 className="text-4xl font-black uppercase tracking-tighter">Ratings and Reviews</h3>
                        <p className="text-xl font-bold text-slate-800 uppercase tracking-widest">Trusted and Verified Globally</p>
                    </div>
                    <div className="slider-track gap-6">
                        {displayReviews.map((rev, idx) => (
                            <div key={idx} className="w-[250px] flex-shrink-0 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between h-48 text-left">
                                <div>
                                    <div className="flex text-yellow-400 text-[10px] mb-2">
                                        {[...Array(rev.stars)].map((_, i) => <i key={i} className="fa-solid fa-star"></i>)}
                                    </div>
                                    <p className="text-lg font-medium italic text-slate-900 line-clamp-3">"{rev.text}"</p>
                                </div>
                                <div className="mt-4 text-navy">
                                    <p className="text-lg font-black uppercase tracking-wider">{rev.name}</p>
                                    <p className="text-[12px] font-bold text-slate-800 uppercase">{rev.role}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        };

        const DashboardAnalytics = ({ invoices }) => {
            const lineRef = useRef(null);
            const barRef = useRef(null);
            const chartInstances = useRef({});

            useEffect(() => {
                const destroyCharts = () => {
                    Object.values(chartInstances.current).forEach(chart => {
                        if (chart) chart.destroy();
                    });
                    chartInstances.current = {};
                };

                destroyCharts();

                const last7Days = [...Array(7)].map((_, i) => {
                    const d = new Date();
                    d.setDate(d.getDate() - i);
                    return d.toISOString().split('T')[0];
                }).reverse();

                const dailySales = last7Days.map(date => {
                    return invoices
                        .filter(inv => inv.created_at && inv.created_at.startsWith(date))
                        .reduce((sum, inv) => sum + (inv.total || 0), 0);
                });

                const commonOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { position: 'bottom', labels: { font: { weight: 'bold', size: 10 }, color: '#000080' } }
                    },
                    scales: {
                        y: { ticks: { color: '#000080', font: { size: 10 } }, grid: { color: '#f1f5f9' } },
                        x: { ticks: { color: '#000080', font: { size: 10 } }, grid: { display: false } }
                    }
                };

                if (lineRef.current) {
                    chartInstances.current.line = new Chart(lineRef.current, {
                        type: 'line',
                        data: {
                            labels: last7Days.map(d => d.split('-').slice(1).reverse().join('/')),
                            datasets: [{
                                label: 'Revenue (₹)',
                                data: dailySales,
                                borderColor: '#000080',
                                backgroundColor: 'rgba(0, 0, 128, 0.1)',
                                fill: true,
                                tension: 0.4,
                                pointBackgroundColor: '#000080',
                                borderWidth: 3
                            }]
                        },
                        options: commonOptions
                    });
                }

                if (barRef.current) {
                    const currentTotal = invoices.reduce((a, b) => a + (b.total || 0), 0);
                    chartInstances.current.bar = new Chart(barRef.current, {
                        type: 'bar',
                        data: {
                            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                            datasets: [
                                { label: 'Sales', data: [42000, 38000, 45000, currentTotal || 52000], backgroundColor: '#000080', borderRadius: 6 },
                                { label: 'Purchases', data: [31000, 35000, 28000, 39000], backgroundColor: '#94a3b8', borderRadius: 6 }
                            ]
                        },
                        options: commonOptions
                    });
                }

                return destroyCharts;
            }, [invoices]);

            return (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-10 text-left">
                    <div className="cyber-card p-8 rounded-[2.5rem]">
                        <h4 className="text-xs font-black uppercase tracking-widest opacity-50 mb-6 text-slate-400">Revenue Growth Trend</h4>
                        <div className="chart-container"><canvas ref={lineRef}></canvas></div>
                    </div>
                    <div className="cyber-card p-8 rounded-[2.5rem]">
                        <h4 className="text-xs font-black uppercase tracking-widest opacity-50 mb-6 text-slate-400">Market Sales vs Procurement</h4>
                        <div className="chart-container"><canvas ref={barRef}></canvas></div>
                    </div>
                </div>
            );
        };

        const App = () => {
            const [tab, setTab] = useState('home');
            const [staff, setStaff] = useState([]);
            const [products, setProducts] = useState([]);
            const [categories, setCategories] = useState([]);
            const [invoices, setInvoices] = useState([]);
            const [cart, setCart] = useState([]);
            const [customerName, setCustomerName] = useState("");
            const [isModalOpen, setIsModalOpen] = useState(false);
            const [newData, setNewData] = useState({});
            const [isEditMode, setIsEditMode] = useState(false);
            const [viewInvoice, setViewInvoice] = useState(null);
            const [viewStaff, setViewStaff] = useState(null);
            const [showSuccessToast, setShowSuccessToast] = useState(false);

            // Invoice Builder States
            const [builderView, setBuilderView] = useState('main'); // main, customer, product
            const [builderPrefix, setBuilderPrefix] = useState('INV-');
            const [builderNum, setBuilderNum] = useState(1);
            const [isBuilderModalOpen, setIsBuilderModalOpen] = useState(false);
            const user = { name: "Admin", picture: "" };
            const getApiUrl = (path) => `${window.location.origin}${path}`;

            useEffect(() => { 
                loadAll(); 
                if (window.lucide) window.lucide.createIcons();
            }, []);
            useEffect(() => {
                if (window.lucide) window.lucide.createIcons();
            }, [tab, builderView, isBuilderModalOpen]);
        
            const loadAll = async () => {
                try {
                    const [s, p, c, i] = await Promise.all([
                        fetch(getApiUrl('/api/staff')).then(r => r.json()).catch(() => []),
                        fetch(getApiUrl('/api/products')).then(r => r.json()).catch(() => []),
                        fetch(getApiUrl('/api/categories')).then(r => r.json()).catch(() => []),
                        fetch(getApiUrl('/api/invoices')).then(r => r.json()).catch(() => [])
                    ]);
                    setStaff(s || []); setProducts(p || []); setCategories(c || []); setInvoices(i || []);
                } catch (e) { console.error("Sync offline."); }
            };

            const openInvoicePopup = async (id) => {
                try {
                    const res = await fetch(`/api/invoices/${id}`);
                    const data = await res.json();
                    setViewInvoice(data); 
                } catch (err) {
                    console.error("Failed to load invoice");
                }};

            const openStaffPopup = (item) => { setViewStaff(item); };
            const downloadPDF = (id) => { window.open(`/api/invoices/${id}/pdf`, '_blank'); };

            const openEditModal = (item) => {
                setNewData({...item});
                setIsEditMode(true);
                setIsModalOpen(true);
            };

            const handleGenericAdd = async (e) => {
                e.preventDefault();
                let endpoint = '';
                let method = isEditMode ? 'PUT' : 'POST';
                
                switch(tab) {
                    case 'staff': endpoint = isEditMode ? `/api/staff/${newData.id}` : '/api/staff'; break;
                    case 'inventory': endpoint = isEditMode ? `/api/products/${newData.id}` : '/api/products'; break;
                    case 'categories': endpoint = isEditMode ? `/api/categories/${newData.id}` : '/api/categories'; break;
                    case 'invoices': endpoint = `/api/invoices/${newData.id}`; break;
                    default: return;
                }

                try {
                    const res = await fetch(endpoint, {
                        method: method,
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(newData)
                    });
                    if (res.ok) {
                        setIsModalOpen(false);
                        setNewData({});
                        setIsEditMode(false);
                        loadAll();
                        setShowSuccessToast(true);
                        setTimeout(() => setShowSuccessToast(false), 3000);
                    }
                } catch (err) {
                    console.error("Failed to process request");
                }
            };

            const addToCart = (product) => {
                if (product.stock <= 0) return;
                const existing = cart.find(i => i.id === product.id);
                if (existing) setCart(cart.map(i => i.id === product.id ? {...i, qty: i.qty + 1} : i));
                else setCart([...cart, {...product, qty: 1}]);
            };

            const generateInvoice = async () => {
                if (!customerName || cart.length === 0) return;
                const total = cart.reduce((sum, i) => sum + (i.price * i.qty), 0);
                const res = await fetch(getApiUrl('/api/invoices'), {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ customer_name: customerName, total, items: cart })
                });
                if (res.ok) { 
                    setCart([]); setCustomerName(""); loadAll(); 
                    setShowSuccessToast(true);
                    setTimeout(() => setShowSuccessToast(false), 4000);
                }
            };

            const deleteItem = async (id) => {
                if (!window.confirm(`Delete registry entry?`)) return;
                let endpoint = '';
                switch(tab) {
                    case 'invoices': endpoint = `/api/invoices/${id}`; break;
                    case 'staff': endpoint = `/api/staff/${id}`; break;
                    case 'inventory': endpoint = `/api/products/${id}`; break;
                    case 'categories': endpoint = `/api/categories/${id}`; break;
                    default: return;
                }
                const res = await fetch(endpoint, { method: 'DELETE' });
                if (res.ok) loadAll();
            };

            const saveBuilderChanges = () => {
                // Sync logic for the builder interface
                setIsBuilderModalOpen(false);
            };

            return (
                <div className="flex flex-col min-h-screen bg-[#f3f4f6]">
                    <header className="w-full glass-header z-50 flex items-center px-10 py-6 text-white shadow-xl text-left">
                        <div className="flex items-center gap-6 mr-12">
                            <img src="/static/Logo2.jpg" alt="Logo" className="h-14 w-auto" onError={(e) => { e.target.onError = null; e.target.src='https://ui-avatars.com/api/?name=TC&background=000080&color=fff'; }}/>
                            <div className="hidden lg:block text-left">
                                <p className="text-lg font-black uppercase tracking-tighter leading-none">Techcraftery</p>
                                <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-blue-300 opacity-70 mt-1">Enterprise Portal</p>
                            </div>
                        </div>

                        <nav className="flex-1 flex items-center gap-3">

                            {['home', 'dashboard', 'billing', 'inventory', 'categories', 'invoices', 'staff','product'].map(id => (

                                <button key={id} onClick={() => { setTab(id); setBuilderView('main'); }} className={`px-6 py-2.5 rounded-xl text-sm font-bold uppercase tracking-widest transition-all ${tab === id ? 'active-tab' : 'hover:bg-white/10 text-white/60'}`}>

                                    {id.charAt(0).toUpperCase() + id.slice(1)}

                                </button>

                            ))}

                        </nav>

                        <div className="flex items-center gap-6 ml-4">
                            <div className="flex items-center gap-4 bg-white/5 px-6 py-2.5 rounded-full border border-white/10 text-white">
                                <img className="w-8 h-8 rounded-full" src="https://ui-avatars.com/api/?name=Admin&background=random" alt="User" />
                                <div className="hidden md:block text-left text-white">
                                    <p className="text-sm font-black uppercase leading-none text-white">{user.name}</p>
                                    <p className="text-[10px] font-bold uppercase text-blue-300 opacity-60">Admin Node</p>
                                </div>
                            </div>
                            <a href="/logout" className="px-6 py-2.5 rounded-full bg-white text-[#000040] text-xs font-black uppercase tracking-widest shadow-md active:scale-95">Logout</a>
                        </div>
                    </header>

                    <main className="flex-1 w-full max-w-screen-2xl mx-auto relative">
                        
                        {tab === 'home' && (
                            <div className="space-y-10 p-10">
                                <header className="mb-14 text-left">
                                    <h2 className="text-6xl md:text-7xl font-black uppercase tracking-tighter italic shimmer inline-block leading-none pr-6">Welcome</h2>
                                    <p className="text-sm font-bold uppercase tracking-widest mt-3 opacity-50 ml-1 text-slate-400">Enterprise Command Center</p>
                                </header>
                                
                                <div className="flex flex-col lg:flex-row gap-6">
                                    <div className="banner-gradient p-10 rounded-3xl flex-1 flex justify-between items-center shadow-sm relative overflow-hidden border border-blue-500">
                                        <div className="z-10 text-left">
                                            <span className="bg-[#000080] text-white text-[10px] font-black px-3 py-1.5 rounded-lg mb-6 inline-block tracking-widest uppercase">NEW FEATURE</span>
                                            <h2 className="font-black text-4xl text-[#000040] uppercase tracking-tighter leading-none text-left">CONVERT DOCUMENTS</h2>
                                            <p className="text-slate-500 text-lg mt-4 max-w-md font-medium leading-relaxed text-left">Streamline your workflow by converting quotations to invoices instantly. Save time on every transaction with our smart mapping engine.</p>
                                            <button className="mt-8 bg-white text-sm font-black px-10 py-4 rounded-2xl border border-slate-200 shadow-sm text-[#000040] hover:bg-slate-50 transition-all uppercase tracking-widest active:scale-95">CONVERT NOW!</button>
                                        </div>
                                        <div className="relative z-10 w-48 h-40 hidden md:flex items-center justify-center opacity-80">
                                             <i className="fa-solid fa-file-invoice text-9xl text-blue-200 absolute top-0 right-0 transform rotate-12"></i>
                                             <i className="fa-solid fa-bolt text-7xl text-[#000080] absolute bottom-4 left-4"></i>
                                        </div>
                                    </div>

                                    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-10 w-full lg:w-1/3 flex flex-col justify-center text-left text-navy">
                                        <div className="flex justify-between items-center mb-8">
                                            <h3 className="font-black text-4xl uppercase tracking-tighter">Performance</h3>
                                        </div>
                                        <div className="flex divide-x divide-slate-100">
                                            <div className="flex-1 pr-6">
                                                <p className="text-slate-800 text-[17px] font-black uppercase tracking-[0.2em]">Total Sales</p>
                                                <p className="text-3xl font-black text-[#000040] mt-3">₹{invoices.reduce((a,b)=>a+(b.total||0),0).toLocaleString()}</p>
                                                <p className="text-green-500 text-[15px] font-bold mt-2 text-left"><i className="fa-solid fa-arrow-up"></i> 100% Session</p>
                                            </div>
                                            <div className="flex-1 pl-6">
                                                <p className="text-slate-800 text-[17px] font-black uppercase tracking-[0.2em]">Purchases</p>
                                                <p className="text-3xl font-black text-[#000040] mt-3">₹0.00</p>
                                                <p className="text-slate-400 text-[15px] font-bold mt-2 italic text-left">Waiting for entry</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-white p-10 rounded-3xl border border-slate-200 shadow-sm text-left">
                                    <div className="flex justify-between items-center mb-10">
                                        <div className="flex items-center space-x-4 text-navy text-left">
                                            <h3 className="font-black text-4xl uppercase tracking-tighter text-left">Quick Create</h3>
                                            <div className="px-3 py-1.5 rounded-lg bg-red-50 flex items-center space-x-2 border border-red-100">
                                                 <i className="fa-solid fa-play text-[10px] text-red-500"></i>
                                                 <span className="text-[15px] font-black text-red-600 uppercase tracking-widest text-left">GUIDE</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-8 text-center text-navy text-left">
                                        {[
                                             {icon: 'fa-regular fa-file-lines', label: 'Invoice', color: 'blue', action: () => setTab('invoice-builder')},
                                            {icon: 'fa-solid fa-cart-shopping', label: 'Purchase'},
                                            {icon: 'fa-solid fa-file-invoice-dollar', label: 'Quotation'},
                                            {icon: 'fa-solid fa-truck', label: 'Challan'},
                                            {icon: 'fa-solid fa-arrow-up-from-bracket', label: 'Credit Note'},
                                            {icon: 'fa-solid fa-cube', label: 'P. Order'},
                                            {icon: 'fa-solid fa-receipt', label: 'Expenses'},
                                            {icon: 'fa-solid fa-file-contract', label: 'Pro Forma'}
                                        ].map((item, idx) => (
                                            <div key={idx} onClick={item.action} className="flex flex-col items-center group cursor-pointer text-center">
                                                <div className={`w-20 h-20 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-center mb-4 group-hover:bg-[#000080] group-hover:border-[#000080] transition-all duration-300 transform group-hover:-translate-y-2 text-left`}>
                                                    <i className={`${item.icon} text-4xl text-navy group-hover:text-white transition-colors`}></i>
                                                </div>
                                                <span className="text-xl font-black uppercase tracking-widest group-hover:text-[#000080] transition-colors text-center">{item.label}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12 text-left">
                                    <div className="bg-white p-10 rounded-3xl border border-slate-200 shadow-sm text-left">
                                        <h3 className="font-black text-4xl text-[#000040] mb-8 uppercase tracking-tighter text-left">Compliance & Logistics</h3>
                                        <div className="grid grid-cols-4 gap-6 text-center text-left">
                                            {[
                                                {icon: 'fa-solid fa-car', label: 'E-way Bill', color: 'text-yellow-600'},
                                                {icon: 'fa-solid fa-file-invoice', label: 'E-Invoice', color: 'text-green-600'},
                                                {icon: 'fa-solid fa-wallet', label: 'Payments', color: 'text-yellow-600'},
                                                {icon: 'fa-solid fa-chart-pie', label: 'Analytics', color: 'text-green-600', action: () => setTab('dashboard')}
                                            ].map((sub, i) => (
                                                <div key={i} onClick={sub.action} className="flex flex-col items-center cursor-pointer group text-left">
                                                    <div className="w-16 h-16 rounded-2xl bg-slate-50 flex items-center justify-center mb-3 group-hover:bg-blue-50 transition-colors border border-transparent group-hover:border-blue-100 text-left">
                                                        <i className={`${sub.icon} text-4xl ${sub.color || 'text-slate-500'} group-hover:text-[#000080] text-left`}></i>
                                                    </div>
                                                    <span className="text-[18px] font-black text-slate-800 uppercase tracking-widest text-left">{sub.label}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="bg-white p-10 rounded-3xl border border-slate-200 shadow-sm text-left">
                                        <h3 className="font-black text-4xl text-[#000040] mb-8 uppercase tracking-tighter text-left">Business Growth</h3>
                                        <div className="grid grid-cols-4 gap-6 text-center text-left">
                                            {[
                                                {icon: 'fa-solid fa-chart-line', label: 'Insights', color: 'text-green-600'},
                                                {icon: 'fa-solid fa-sack-dollar', label: 'Rewards', color: 'text-yellow-600'},
                                                {icon: 'fa-solid fa-file-pen', label: 'Templates', color: 'text-green-600'},
                                                {icon: 'fa-solid fa-gear', label: 'Settings', color: 'text-yellow-600'}
                                            ].map((sub, i) => (
                                                <div key={i} className="flex flex-col items-center cursor-pointer group text-left">
                                                    <div className="w-16 h-16 rounded-2xl bg-slate-50 flex items-center justify-center mb-3 group-hover:bg-blue-50 transition-colors border border-transparent group-hover:border-blue-100 text-left">
                                                        <i className={`${sub.icon} text-4xl ${sub.color || 'text-slate-800'} group-hover:text-[#000080] text-left`}></i>
                                                    </div>
                                                    <span className="text-[18px] font-black text-slate-800 uppercase tracking-widest text-left">{sub.label}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col lg:flex-row items-center justify-between gap-8 p-10 bg-[#000040] rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden group text-left">
                                    <div className="absolute top-0 right-0 w-64 h-64 bg-[#000080] blur-[120px] opacity-30 group-hover:opacity-50 transition-opacity text-left"></div>
                                    <div className="flex items-center space-x-8 z-10 text-left text-white">
                                        <div className="bg-white/10 rounded-2xl p-6 backdrop-blur-xl border border-white/10 text-left">
                                            <i className="fa-solid fa-rocket text-blue-400 text-3xl text-left"></i>
                                        </div>
                                        <div className="text-left text-white">
                                            <h4 className="text-2xl font-black uppercase tracking-tighter text-left">Techcraftery Premium Offer</h4>
                                            <p className="text-slate-400 font-medium text-lg mt-1 text-left">Claim your exclusive ₹500 discount on annual enterprise nodes.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-8 z-10 text-left">
                                        <div className="hidden sm:flex items-center space-x-4 bg-white/5 px-5 py-3 rounded-2xl border border-white/10 text-left">
                                            <div className="flex -space-x-3 text-left">
                                                <img className="w-10 h-10 rounded-full border-2 border-[#000040]" src="https://ui-avatars.com/api/?name=1&background=random" alt="U" />
                                                <img className="w-10 h-10 rounded-full border-2 border-[#000040]" src="https://ui-avatars.com/api/?name=2&background=random" alt="U" />
                                                <img className="w-10 h-10 rounded-full border-2 border-[#000040]" src="https://ui-avatars.com/api/?name=3&background=random" alt="U" />
                                            </div>
                                            <span className="text-xs text-slate-300 font-black uppercase tracking-widest leading-none text-left">20 Lakh+ Nodes</span>
                                        </div>
                                        <button className="bg-white hover:bg-slate-100 text-[#000040] px-12 py-5 rounded-2xl font-black text-sm shadow-2xl transition-all transform active:scale-95 uppercase tracking-widest text-left">UPGRADE NOW</button>
                                    </div>
                                </div>

                                <ReviewSlider />
                            </div>
                        )}

                        {tab === 'invoice-builder' && (
                            <div className="fade-in">
                                {builderView === 'main' && (
                                    <div id="builder-app" className="flex flex-col min-h-screen bg-[#F3F4F7]">
                                        <header className="p-4 bg-white border-b flex justify-between items-center px-8 z-30 sticky top-0 shadow-sm">
                                            <div className="flex items-center gap-6">
                                                <div className="bg-[#3b82f6] p-2 rounded-lg">
                                                    <i data-lucide="file-text" className="w-6 h-6 text-white"></i>
                                                </div>
                                                <div className="text-left">
                                                    <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider leading-none mb-1">Invoice #</p>
                                                    <div className="flex items-center gap-3">
                                                        <h1 className="text-xl font-bold text-gray-800 leading-none">{builderPrefix}{builderNum}</h1>
                                                        <p className="text-sm text-gray-500 leading-none">01-01-2026</p>
                                                    </div>
                                                </div>

                                            </div>
                                            <div className="flex items-center gap-4">
                                                <button onClick={() => setIsBuilderModalOpen(true)} className="text-[#3b82f6] font-semibold text-sm px-4 py-2 hover:bg-blue-50 rounded-lg transition-colors">Edit</button>
                                                <button className="bg-[#3b82f6] text-white font-bold text-sm px-6 py-2 rounded-lg shadow-lg shadow-blue-100 hover:bg-blue-700 transition-all active:scale-95">Download PDF</button>
                                            </div>
                                        </header>

                                        <main className="flex-1 flex justify-center w-full p-8">
                                            <div className="w-full flex flex-col gap-4 overflow-y-auto builder-scroll">
                                                <div className="p-6 flex items-center gap-4 bg-white rounded-xl border border-gray-100 shadow-sm">
                                                    <input type="checkbox" className="w-6 h-6 rounded border-gray-300 text-[#000040] focus:ring-0" />
                                                    <label className="text-base font-semibold text-gray-700">Export Invoice/SEZ</label>
                                                </div>

                                                <div className="bg-white px-6 py-6 rounded-xl border border-gray-100 shadow-sm text-left">
                                                    <div className="flex items-center gap-1 mb-4">
                                                        <span className="text-sm font-bold text-gray-800 uppercase tracking-widest">Customer</span>
                                                        <i data-lucide="info" className="w-4 h-4 text-gray-400"></i>
                                                    </div>
                                                    <button onClick={() => setBuilderView('customer')} className="w-full border-2 border-dashed border-gray-200 rounded-lg py-16 flex items-center justify-center gap-3 text-[#3b82f6] font-bold text-lg hover:bg-blue-50 transition-colors">
                                                        <i data-lucide="circle-plus" className="w-6 h-6"></i>
                                                        Select Customer
                                                    </button>
                                                </div>

                                                <div className="bg-white px-6 py-6 rounded-xl border border-gray-100 shadow-sm text-left">
                                                    <div className="flex items-center gap-1 mb-4">
                                                        <span className="text-sm font-bold text-gray-800 uppercase tracking-widest">Products</span>
                                                        <i data-lucide="info" className="w-4 h-4 text-gray-400"></i>
                                                    </div>
                                                    <button onClick={() => setBuilderView('product')} className="w-full border-2 border-dashed border-gray-200 rounded-lg py-16 flex items-center justify-center gap-3 text-[#3b82f6] font-bold text-lg hover:bg-blue-50 transition-colors">
                                                        <i data-lucide="circle-plus" className="w-6 h-6"></i>
                                                        Select Products
                                                    </button>
                                                </div>

                                                <div className="p-6 bg-blue-50 rounded-xl border border-blue-100 flex items-center justify-between text-left">
                                                    <div>
                                                        <h3 className="text-blue-900 font-black text-lg">Add Custom Fields</h3>
                                                        <p className="text-blue-700 text-sm font-medium">Personalize every detail to perfectly suit your style.</p>
                                                    </div>
                                                    <div className="bg-white p-3 rounded-full shadow-md">
                                                        <i data-lucide="headphones" className="w-6 h-6 text-blue-500"></i>
                                                    </div>
                                                </div>

                                                <div className="pt-6 pb-2 flex justify-between items-center">
                                                    <span className="text-xs font-black text-gray-400 uppercase tracking-widest">Optional Sections</span>
                                                    <button className="text-xs font-black text-gray-400 flex items-center gap-2 hover:text-gray-600 transition-colors uppercase">
                                                        <i data-lucide="circle-plus" className="w-4 h-4"></i> Additional Charges
                                                    </button>
                                                </div>

                                                <div className="bg-white divide-y divide-gray-100 rounded-xl border border-gray-100 overflow-hidden shadow-sm mb-12 text-left">
                                                    {[
                                                        { label: 'Select Dispatch Address', icon: 'truck' },
                                                        { label: 'Bank Account', sub: 'Cash', icon: 'landmark', action: 'Change' },
                                                        { label: 'Select Signature', icon: 'pen-tool' },
                                                        { label: 'Add Reference', icon: 'layers' },
                                                        { label: 'Add Notes', icon: 'file-text' },
                                                        { label: 'Add Terms', icon: 'book-open' },
                                                        { label: 'Add Extra Discount', icon: 'percent' },
                                                        { label: 'Delivery/Shipping Charges', isRupee: true },
                                                        { label: 'Packaging', isRupee: true }
                                                    ].map((row, idx) => (
                                                        <div key={idx} className="px-6 py-6 flex items-center gap-6 hover:bg-gray-50 cursor-pointer transition-colors group">
                                                            {row.isRupee ? (
                                                                <RupeeCoinSVG className="w-6 h-6 text-gray-400 group-hover:text-[#3b82f6] transition-colors" />
                                                            ) : (
                                                                <i data-lucide={row.icon} className="w-6 h-6 text-gray-400 group-hover:text-[#3b82f6] transition-colors"></i>
                                                            )}
                                                            <div className="flex-1">
                                                                {row.sub && <p className="text-[10px] text-gray-400 font-bold uppercase mb-1">{row.label}</p>}
                                                                <p className={`text-base font-semibold ${row.sub ? 'text-gray-800' : 'text-gray-600'}`}>{row.sub || row.label}</p>
                                                            </div>
                                                            {row.action ? (
                                                                <button className="text-[#3b82f6] font-black text-sm uppercase">{row.action}</button>
                                                            ) : (
                                                                <i data-lucide="plus" className="w-5 h-5 text-gray-300"></i>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </main>

                                        {isBuilderModalOpen && (
                                            <div className="fixed inset-0 z-[150] flex items-center justify-center p-8 bg-gray-900/60 backdrop-blur-sm">
                                                <div className="bg-white rounded-[2.5rem] p-12 w-[600px] shadow-2xl relative text-left">
                                                    <div className="flex justify-between items-center mb-10">
                                                        <h2 className="text-3xl font-black text-gray-800 tracking-tight">Edit Document Meta</h2>
                                                        <button onClick={() => setIsBuilderModalOpen(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors"><i data-lucide="x" className="w-7 h-7 text-gray-400"></i></button>
                                                    </div>

                                                    <div className="space-y-10">
                                                        <div>
                                                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">Prefix</label>
                                                            <div className="flex items-center border-b-2 border-gray-100 focus-within:border-[#3b82f6] transition-colors py-4">
                                                                <input type="text" value={builderPrefix} onChange={e => setBuilderPrefix(e.target.value)} className="flex-1 text-2xl font-bold bg-transparent outline-none" />
                                                                <button className="text-[#3b82f6] text-sm font-black uppercase">Change</button>
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">Document Number</label>
                                                            <div className="border-b-2 border-gray-100 focus-within:border-[#3b82f6] transition-colors py-4">
                                                                <input type="number" value={builderNum} onChange={e => setBuilderNum(e.target.value)} className="w-full text-2xl font-bold bg-transparent outline-none" />
                                                            </div>
                                                        </div>
                                                        <button onClick={saveBuilderChanges} className="w-full bg-[#3b82f6] text-white font-black py-6 rounded-2xl shadow-xl shadow-blue-200 active:scale-[0.98] transition-all hover:bg-blue-700 text-lg">
                                                            Apply Settings
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {builderView === 'customer' && (
                                    <div className="fixed inset-0 bg-white z-[100] flex flex-col fade-in">
                                        <div className="pt-32 p-8 flex items-center gap-8 border-b max-w-7xl mx-auto w-full">
                                            <button onClick={() => setBuilderView('main')} className="p-3 hover:bg-gray-100 rounded-full transition-colors"><i data-lucide="arrow-left" className="w-8 h-8 text-gray-600"></i></button>
                                            <div className="flex-1 bg-gray-100 rounded-2xl flex items-center px-6 py-4 gap-4">
                                                <i data-lucide="search" className="w-6 h-6 text-gray-400"></i>
                                                <input type="text" placeholder="Search Customer" className="bg-transparent text-xl w-full outline-none" />
                                            </div>
                                        </div>
                                        <button className="max-w-7xl mx-auto w-full p-8 text-[#3b82f6] font-black text-2xl flex items-center gap-4 border-b hover:bg-blue-50 transition-colors">
                                            <i data-lucide="circle-plus" className="w-8 h-8"></i> Add new customer
                                        </button>
                                        <div className="flex-1 overflow-y-auto p-4 flex flex-col items-center justify-center text-gray-400">
                                            <i data-lucide="users" className="w-24 h-24 mb-6 opacity-20"></i>
                                            <p className="text-2xl font-medium">Search to find a customer</p>
                                        </div>
                                    </div>
                                )}

                                {builderView === 'product' && (
                                    <div className="fixed inset-0 bg-white z-[100] flex flex-col fade-in">
                                        <div className=" pt-32 p-8 flex items-center gap-8 border-b max-w-7xl mx-auto w-full">
                                            <button onClick={() => setBuilderView('main')} className="p-3 hover:bg-gray-100 rounded-full transition-colors"><i data-lucide="arrow-left" className="w-8 h-8 text-gray-600"></i></button>
                                            <div className="flex-1 bg-gray-100 rounded-2xl flex items-center px-6 py-4 gap-4">
                                                <i data-lucide="search" className="w-6 h-6 text-gray-400"></i>
                                                <input type="text" placeholder="Search Product" className="bg-transparent text-xl w-full outline-none" />
                                            </div>
                                        </div>

                                        <button className="max-w-7xl mx-auto w-full p-8 text-[#3b82f6] font-black text-2xl flex items-center gap-4 border-b hover:bg-blue-50 transition-colors text-left">
                                            <i data-lucide="circle-plus" className="w-8 h-8"></i> Add New Product
                                        </button>
                                        <div className="flex-1 overflow-y-auto max-w-7xl mx-auto w-full p-8">
                                            <div className="p-10 border border-gray-100 rounded-3xl bg-gray-50 flex justify-between items-center group hover:border-blue-200 cursor-pointer transition-all text-left">
                                                <div>
                                                    <h4 className="font-black text-gray-800 text-2xl">Sample Product</h4>
                                                    <p className="text-xl text-gray-500 font-medium">₹100</p>
                                                    <button className="text-base text-[#3b82f6] font-black mt-4 uppercase tracking-wider">Edit Details</button>
                                                </div>

                                                <div className="flex flex-col items-end">
                                                    <span className="text-xs text-gray-400 bg-white border px-4 py-1 rounded-full mb-4 uppercase font-black tracking-widest">In Stock</span>
                                                    <div className="flex items-center gap-8 bg-white border border-gray-200 rounded-full p-2 shadow-sm">
                                                        <button className="w-12 h-12 flex items-center justify-center text-gray-400 hover:bg-gray-50 rounded-full"><i data-lucide="minus" className="w-6 h-6"></i></button>
                                                        <span className="text-2xl font-black text-gray-700 w-6 text-center">0</span>
                                                        <button className="w-12 h-12 flex items-center justify-center bg-[#3b82f6] text-white rounded-full shadow-lg shadow-blue-200"><i data-lucide="plus" className="w-6 h-6"></i></button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {tab === 'dashboard' && (
                            <div className="space-y-12 pb-20 p-10 text-left">
                                <header className="mb-14">
                                    <h2 className="text-6xl md:text-7xl font-black uppercase tracking-tighter italic shimmer inline-block leading-none pr-6 text-left">Analytics</h2>
                                    <p className="text-sm font-bold uppercase tracking-widest mt-3 opacity-50 ml-1 text-slate-400 text-left">Operational Analytics Node v2.5</p>
                                </header>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-left">
                                    <div className="cyber-card p-10 rounded-[2.5rem] text-left">
                                        <p className="text-[14px] font-black uppercase mb-1 opacity-60 tracking-wider text-left">Total Sales Revenue</p>
                                        <p className="text-5xl font-black text-navy text-left">₹{invoices.reduce((a,b)=>a+(b.total||0),0).toLocaleString()}</p>
                                    </div>
                                    <div className="cyber-card p-10 rounded-[2.5rem] text-left">
                                        <p className="text-[14px] font-black uppercase mb-1 opacity-60 tracking-wider text-left">Inventory Assets</p>
                                        <p className="text-5xl font-black text-navy text-left">{products.length}</p>
                                    </div>
                                    <div className="cyber-card p-10 rounded-[2.5rem] text-left">
                                        <p className="text-[14px] font-black uppercase mb-1 opacity-60 tracking-wider text-left">Staff Directory</p>
                                        <p className="text-5xl font-black text-navy text-left">{staff.length}</p>
                                    </div>
                                </div>

                                <DashboardAnalytics invoices={invoices} />
                            </div>
                        )}

                        {tab === 'billing' && (
                            <div className="space-y-12 pb-20 p-10 text-left text-navy">
                                <header className="mb-14 text-left">
                                    <h2 className="text-6xl md:text-7xl font-black uppercase tracking-tighter italic shimmer inline-block leading-none pr-6 text-left">Billing</h2>
                                    <p className="text-sm font-bold uppercase tracking-widest mt-3 opacity-50 ml-1 text-slate-400 text-left text-left">Transaction Authorization Gateway</p>
                                </header>
                                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 text-left">
                                    <div className="lg:col-span-8 space-y-8 text-left text-navy">
                                        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6 text-left text-navy">
                                            {products.map(p => (
                                                <button key={p.id} onClick={() => addToCart(p)} className="cyber-card p-8 rounded-[2.5rem] text-left hover:border-blue-400 group transition-all text-left text-navy">
                                                    <p className="text-[13px] font-black uppercase mb-2 opacity-40 text-left">{p.category_name}</p>
                                                    <p className="font-black text-2xl mb-4 leading-tight text-left">{p.name}</p>
                                                    <div className="flex justify-between items-center text-left text-navy">
                                                        <p className="font-black text-blue-700 text-xl text-left text-navy">₹{p.price}</p>
                                                        <p className={`text-[10px] font-bold uppercase px-3 py-1 rounded-full ${p.stock < 10 ? 'bg-red-50 text-red-500' : 'bg-blue-50 text-gray-400'} text-left text-navy text-left`}>Stock: {p.stock}</p>
                                                    </div>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="lg:col-span-4 text-left text-navy">
                                        <div className="cyber-card p-10 rounded-[3rem] sticky top-10 text-left text-navy">
                                            <h3 className="text-3xl font-black uppercase mb-8 italic text-[#000080] text-left text-navy">Billing Cart</h3>
                                            <input type="text" placeholder="Customer Name" value={customerName} onChange={e => setCustomerName(e.target.value)} className="w-full bg-blue-50 border border-blue-100 p-5 rounded-2xl mb-8 outline-none focus:border-blue-800 text-lg font-bold text-navy text-left text-navy" />
                                            <div className="billing-cart-area space-y-5 mb-8 text-left text-navy">
                                                {cart.map(item => (
                                                    <div key={item.id} className="flex justify-between items-center border-b border-blue-50 pb-3 text-left text-navy">
                                                        <div className="text-left text-navy text-left text-navy"><p className="text-xl font-black text-left text-navy">{item.name}</p><p className="text-[11px] font-bold opacity-50 uppercase text-left text-navy">{item.qty} units x ₹{item.price}</p></div>
                                                        <p className="text-xl font-black text-left text-navy text-left text-navy text-left text-navy text-left text-navy text-left text-navy text-left text-navy">₹{item.qty * item.price}</p>
                                                    </div>
                                                ))}
                                            </div>
                                            <div className="pt-8 border-t border-blue-100 space-y-6 text-left text-navy text-left text-navy">
                                                <div className="flex justify-between font-black text-2xl text-left text-navy text-left text-navy text-left text-navy text-left text-navy"><span>TOTAL</span><span className="text-blue-800 text-left text-navy text-left text-navy text-left text-navy">₹{cart.reduce((s,i)=>s+(i.qty*i.price), 0)}</span></div>
                                                <button onClick={generateInvoice} disabled={cart.length === 0 || !customerName} className="w-full py-5 bg-[#000080] text-white rounded-2xl font-black uppercase text-sm tracking-[0.2em] shadow-lg hover:bg-[#000040] text-white text-left text-navy text-center">Generate Invoice</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {['inventory', 'staff', 'categories', 'invoices'].includes(tab) && (
                            <div className="space-y-12 pb-20 p-10 text-left text-navy">
                                <header className="mb-14 flex justify-between items-end text-left text-navy">
                                    <div className="text-left text-navy">
                                        <h2 className="text-6xl md:text-7xl font-black uppercase tracking-tighter italic shimmer inline-block leading-none pr-6 text-left text-navy">{tab.charAt(0).toUpperCase() + tab.slice(1)}</h2>
                                        <p className="text-sm font-bold uppercase tracking-widest mt-3 opacity-50 ml-1 text-slate-400 text-left text-navy uppercase text-left">Registry Asset Management</p>
                                    </div>
                                    <div className="flex gap-4 mb-2 text-left text-navy">
                                        {tab === 'invoices' ? (
                                            <button onClick={() => setTab('billing')} className="bg-[#000080] text-white px-8 py-4 rounded-[1.5rem] font-black uppercase text-[13px] tracking-widest shadow-xl shadow-blue-900/10 hover:bg-[#000040] transition-all active:scale-95 text-white text-left text-navy">
                                                <i className="fa-solid fa-plus mr-2 text-white"></i> Create Invoice
                                            </button>
                                        ) : (
                                            <button onClick={() => {setNewData({}); setIsEditMode(false); setIsModalOpen(true);}} className="bg-[#000080] text-white px-8 py-4 rounded-[1.5rem] font-black uppercase text-[13px] tracking-widest shadow-xl shadow-blue-900/10 hover:bg-[#000040] transition-all active:scale-95 text-white text-left text-navy">
                                                <i className="fa-solid fa-plus mr-2 text-white"></i> Add {tab === 'inventory' ? 'Stock' : tab === 'staff' ? 'Staff' : 'Entry'}
                                            </button>
                                        )}
                                    </div>
                                </header>
                                <div className="cyber-card rounded-[2.5rem] overflow-hidden mb-24 text-left text-navy">
                                    <div className="overflow-x-auto text-left text-navy">
                                        <table className="w-full text-left min-w-[900px] text-left text-navy">
                                            <thead className="bg-blue-50 border-b border-blue-100 text-left text-navy">
                                                <tr className="text-left text-navy text-left text-navy">
                                                    <th className="px-10 py-6 text-[14px] font-black uppercase tracking-widest text-left text-navy">Entry Name</th>
                                                    <th className="px-10 py-6 text-[14px] font-black uppercase tracking-widest text-left text-navy text-left text-navy">Registry Data</th>
                                                    <th className="px-10 py-6 text-[14px] font-black uppercase tracking-widest text-left text-navy text-left text-navy">Valuation / Status</th>
                                                    <th className="px-10 py-6 text-[14px] font-black uppercase tracking-widest text-right text-navy text-left text-navy">Ops</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-blue-50 text-left text-navy">
                                                {(tab==='inventory' ? products : tab==='staff' ? staff : tab==='categories' ? categories : invoices).map(item => (
                                                    <tr key={item.id} className="text-left text-navy">
                                                        <td className="px-10 py-6 font-black text-xl text-zinc-800 text-left text-navy">{item.name || item.customer_name}</td>
                                                        <td className="px-10 py-6 text-[15px] uppercase font-bold opacity-60 text-left text-navy text-left text-navy">{item.role || item.stock || item.created_at || 'Verified'}</td>
                                                        <td className="px-10 py-6 font-black text-2xl text-blue-700 text-left text-navy text-left text-navy"> {item.total ? '₹'+item.total : item.price ? '₹'+item.price : 'ACTIVE'}</td>
                                                        <td className="px-10 py-6 text-right space-x-4 text-left text-navy text-left text-navy">
                                                            <button onClick={() => tab === 'invoices' ? openInvoicePopup(item.id) : openStaffPopup(item)} className="text-blue-800 text-sm font-black uppercase underline decoration-2 underline-offset-4 text-left text-navy">View</button>
                                                            <button onClick={() => openEditModal(item)} className="text-blue-500 text-sm font-black uppercase hover:underline decoration-2 underline-offset-4 text-left text-navy">Edit</button>
                                                            {tab === 'invoices' && <button onClick={() => downloadPDF(item.id)} className="text-emerald-600 text-sm font-black uppercase hover:underline decoration-2 underline-offset-4 text-left text-navy text-left text-navy">PDF</button>}
                                                            <button onClick={() => deleteItem(item.id)} className="text-red-500 text-sm font-black uppercase hover:underline decoration-2 underline-offset-4 text-left text-navy text-left text-navy">Delete</button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        )}
                    </main>

                    {/* Generic ERP Modal */}
                    {isModalOpen && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-[#000040]/80 backdrop-blur-md overflow-y-auto text-navy text-left">
                            <div className="w-full max-w-lg bg-white p-12 rounded-[3rem] shadow-2xl border border-blue-100 my-auto text-left">
                                <h3 className="text-3xl font-black mb-8 uppercase italic text-left text-navy">{isEditMode ? 'Update' : 'Provision'} {tab.charAt(0).toUpperCase() + tab.slice(1).replace('ies', 'y')}</h3>
                                <form onSubmit={handleGenericAdd} className="space-y-5 text-left text-navy text-left text-navy text-left text-navy">
                                    <div className="w-full text-left text-navy">
                                        <label className="text-[10px] font-black uppercase opacity-50 ml-2 text-left text-navy">Name</label>
                                        <input type="text" placeholder="Identity Label" required value={newData.name || newData.customer_name || ''} className="w-full p-5 bg-blue-50 border border-blue-100 rounded-2xl outline-none focus:border-blue-800 text-md font-bold text-navy text-left text-navy text-left text-navy" 
                                            onChange={e => setNewData(tab === 'invoices' ? {...newData, customer_name: e.target.value} : {...newData, name: e.target.value})} />
                                    </div>
                                    
                                    {tab === 'inventory' && (
                                        <div className="text-left text-navy">
                                            <div className="w-full text-left text-navy">
                                                <label className="text-[10px] font-black uppercase opacity-50 ml-2 text-left text-navy text-left text-navy">Target Category</label>
                                                <select required value={newData.category_id || ''} className="w-full p-5 bg-blue-50 border border-blue-100 rounded-2xl outline-none focus:border-blue-800 text-md font-bold text-[#000080] text-left text-navy text-left text-navy" onChange={e => setNewData({...newData, category_id: e.target.value})}>
                                                    <option value="">Select Category</option>
                                                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                                </select>
                                            </div>
                                            <div className="flex gap-5 text-left text-navy">
                                                <div className="w-1/2 text-left text-navy">
                                                    <label className="text-[10px] font-black uppercase opacity-50 ml-2 text-left text-navy text-left text-navy">Price (₹)</label>
                                                    <input type="number" placeholder="Price" value={newData.price || ''} className="w-full p-5 bg-blue-50 border border-blue-100 rounded-2xl text-md font-bold text-navy text-left text-navy text-left text-navy" onChange={e => setNewData({...newData, price: e.target.value})} />
                                                </div>
                                                <div className="w-1/2 text-left text-navy">
                                                    <label className="text-[10px] font-black uppercase opacity-50 ml-2 text-left text-navy text-left text-navy text-left text-navy">Stock Units</label>
                                                    <input type="number" placeholder="Stock" value={newData.stock || ''} className="w-full p-5 bg-blue-50 border border-blue-100 rounded-2xl text-md font-bold text-navy text-left text-navy text-left text-navy text-left text-navy" onChange={e => setNewData({...newData, stock: e.target.value})} />
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {tab === 'staff' && (
                                        <div className="w-full text-left text-navy text-left text-navy">
                                            <label className="text-[10px] font-black uppercase opacity-50 ml-2 text-left text-navy text-left text-navy">Designation</label>
                                            <input type="text" placeholder="Designation" required value={newData.role || ''} className="w-full p-5 bg-blue-50 border border-blue-100 rounded-2xl text-md font-bold text-navy text-left text-navy text-left text-navy" onChange={e => setNewData({...newData, role: e.target.value})} />
                                        </div>
                                    )}
                                    
                                    <div className="flex gap-5 pt-6 text-left text-navy">
                                        <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 py-5 bg-gray-100 rounded-2xl font-black uppercase text-xs tracking-widest active:scale-95 text-navy text-center">Abort</button>
                                        <button type="submit" className="flex-1 py-5 bg-[#000080] text-white rounded-2xl font-black uppercase text-xs tracking-widest shadow-lg active:scale-95 text-white text-center"> {isEditMode ? 'Update' : 'Execute'}</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    )}
  
{tab === 'product' && (
  <div className="p-10 fade-in">
    <div className="flex justify-between items-center mb-10">
      <h2 className="text-5xl font-black uppercase tracking-tighter text-[#000040]">
        Product Management
      </h2>
      <button
        onClick={() => setIsModalOpen(true)}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        + Add Product
      </button>
    </div>

    {/* Product Table */}
    <table className="w-full text-left border">
      <thead>
        <tr className="bg-blue-100">
          <th className="p-3">Product Name</th>
          <th className="p-3">Category</th>
          <th className="p-3">Price</th>
          <th className="p-3">Actions</th>
        </tr>
      </thead>
      <tbody>
        {products.map((product, index) => (
          <tr key={index} className="border-t">
            <td className="p-3">{product.name}</td>
            <td className="p-3">{product.category}</td>
            <td className="p-3">₹{product.price}</td>
            <td className="p-3">
              <button className="text-blue-600 mr-2">Edit</button>
              <button className="text-red-600">Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>

    {/* Modal for Adding Product */}
    {isModalOpen && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div className="bg-white p-6 rounded shadow-lg w-1/3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setProducts([...products, newData]);
              setNewData({});
              setIsModalOpen(false);
            }}
          >
            <label className="block text-xs font-bold uppercase mb-2">Product Name</label>
            <input
              type="text"
              required
              value={newData.name || ''}
              onChange={(e) => setNewData({ ...newData, name: e.target.value })}
              className="w-full p-3 mb-4 bg-blue-50 border border-blue-100 rounded"
            />

            <label className="block text-xs font-bold uppercase mb-2">Category</label>
            <input
              type="text"
              required
              value={newData.category || ''}
              onChange={(e) => setNewData({ ...newData, category: e.target.value })}
              className="w-full p-3 mb-4 bg-blue-50 border border-blue-100 rounded"
            />

            <label className="block text-xs font-bold uppercase mb-2">Price</label>
            <input
              type="number"
              required
              value={newData.price || ''}
              onChange={(e) => setNewData({ ...newData, price: e.target.value })}
              className="w-full p-3 mb-4 bg-blue-50 border border-blue-100 rounded"
            />

            <div className="flex gap-5 pt-6">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="flex-1 py-3 bg-gray-100 rounded font-bold uppercase text-xs tracking-widest"
              >
                Abort
              </button>
              <button
                type="submit"
                className="flex-1 py-3 bg-[#000080] text-white rounded font-bold uppercase text-xs tracking-widest shadow-lg"
              >
                Execute
              </button>
            </div>
          </form>
        </div>
      </div>
    )}
  </div>
)}

   

                    {/* Support Button */}
                    <div className="fixed bottom-8 right-8 z-50 text-left text-white">
                         <button className="bg-[#000080] hover:bg-[#000040] text-white w-20 h-20 rounded-full flex items-center justify-center shadow-2xl transition-all transform hover:scale-110 group text-white">
                            <i className="fa-solid fa-headset text-3xl group-hover:rotate-12 transition-transform text-white text-left"></i>
                        </button>
                    </div>

                    {/* Restore View Modal logic */}
                    {viewInvoice && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-[#000040]/80 backdrop-blur-md overflow-y-auto text-navy text-left">
                            <div className="w-full max-w-2xl bg-white p-12 rounded-[3.5rem] relative border border-blue-100 shadow-3xl my-10 text-left">
                                <h3 className="text-4xl font-black mb-6 text-[#000080] tracking-tighter uppercase font-black text-left">Invoice: #{viewInvoice.invoice.id}</h3>
                                <div className="space-y-2 mb-10 border-l-4 border-blue-800 pl-6 text-left">
                                    <p className="text-xl font-bold text-left">Client Entity: <span className="text-[#000080]">{viewInvoice.invoice.customer_name}</span></p>
                                    <p className="text-[12px] font-black uppercase opacity-60 text-left">Authorized Timestamp: {new Date(viewInvoice.invoice.created_at).toLocaleString()}</p>
                                </div>
                                <div className="overflow-hidden rounded-3xl border border-blue-50 mb-10 text-left">
                                    <table className="w-full text-left">
                                        <thead className="bg-blue-50 font-black uppercase text-[11px] tracking-widest text-left">
                                            <tr>
                                                <th className="px-8 py-4 text-left text-navy">Item</th>
                                                <th className="px-8 py-4 text-center text-navy">Qty</th>
                                                <th className="px-8 py-4 text-right text-navy">Sum</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-blue-50 text-left">
                                            {(viewInvoice.items || []).map(item => (
                                                <tr key={item.id} className="text-left text-navy">
                                                    <td className="px-8 py-4 font-black text-lg text-left text-navy">{item.name}</td>
                                                    <td className="px-8 py-4 text-center font-bold opacity-70 text-navy">{item.quantity}</td>
                                                    <td className="px-8 py-4 font-black text-right text-blue-900 text-navy">₹{item.price * item.quantity}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="flex justify-between items-center bg-[#000040] p-8 rounded-3xl text-white text-left">
                                    <p className="text-[13px] font-black uppercase tracking-widest opacity-60 text-left text-white">Total Valuation</p>
                                    <p className="text-4xl md:text-5xl font-black text-left text-white">₹{viewInvoice.items.reduce((s,i)=>s+(i.price*i.quantity),0)}</p>
                                </div>
                                <button onClick={() => setViewInvoice(null)} className="absolute top-10 right-10 w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center font-bold text-[#000080] hover:bg-red-50 hover:text-red-500 transition-all text-xl shadow-sm text-navy">✕</button>
                            </div>
                        </div>
                    )}

                    {viewStaff && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-[#000040]/80 backdrop-blur-md overflow-y-auto">
                            <div className="w-full max-w-lg bg-white p-12 rounded-[3.5rem] relative border border-blue-100 shadow-3xl my-10 text-left text-navy">
                                <div className="flex flex-col items-center text-center space-y-6 text-navy">
                                    <img className="w-32 h-32 rounded-full border-4 border-blue-50 text-navy" src={`https://ui-avatars.com/api/?name=${viewStaff.name}&background=000080&color=fff&size=200`} alt="Staff" />
                                    <div className="text-navy text-center">
                                        <h3 className="text-4xl font-black text-[#000080] tracking-tighter uppercase text-navy text-center">{viewStaff.name}</h3>
                                        <p className="text-lg font-bold text-slate-400 uppercase tracking-widest mt-2 text-navy text-center">{viewStaff.role}</p>
                                    </div>
                                    <div className="w-full grid grid-cols-2 gap-4 pt-6 text-navy text-center">
                                        <div className="bg-blue-50 p-6 rounded-3xl text-navy">
                                            <p className="text-[10px] font-black uppercase opacity-60 mb-2 text-navy">Registry ID</p>
                                            <p className="text-xl font-black text-[#000080] text-navy">#{viewStaff.id}</p>
                                        </div>
                                        <div className="bg-emerald-50 p-6 rounded-3xl text-navy">
                                            <p className="text-[10px] font-black uppercase opacity-60 mb-2 text-navy">Status</p>
                                            <p className="text-xl font-black text-emerald-600 text-navy">Active</p>
                                        </div>
                                    </div>
                                </div>
                                <button onClick={() => setViewStaff(null)} className="absolute top-10 right-10 w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center font-bold text-[#000080] hover:bg-red-50 hover:text-red-500 transition-all text-xl shadow-sm text-navy">✕</button>
                            </div>
                        </div>
                    )}
                </div>
            );
        };

        const container = document.getElementById('root');
        const root = ReactDOM.createRoot(container);
        root.render(<App />);
    </script>
</body>
</html>
