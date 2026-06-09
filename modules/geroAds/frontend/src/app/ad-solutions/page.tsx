'use client'
import { useState } from 'react'
import Link from 'next/link'

const solutions = [
  {
    icon: 'store',
    title: 'Indexation Organique',
    tag: 'Gratuit',
    tagClass: '',
    desc: 'Tous les commerces du Terminal 2F sont référencés gratuitement. Si une enseigne est la plus proche géographiquement du besoin exprimé, elle est citée prioritairement.',
    points: ['Référencement automatique', 'Priorité géographique', 'Aucun coût'],
  },
  {
    icon: 'sell',
    title: 'Enchères Contextuelles',
    tag: 'Premium',
    tagClass: 'premium',
    desc: 'Les grandes enseignes misent sur des flux massifs : retards de vols, correspondances spécifiques,高峰期. Le plus offrant gagne la visibilité vocale.',
    points: ['Ciblage par intention vocale', 'Enchères en temps réel', 'Budget maîtrisé'],
  },
  {
    icon: 'handyman',
    title: 'Boost Artisans & Niche',
    tag: 'Solidaire',
    tagClass: 'boost',
    desc: '20% des interactions sont sanctuarisées pour faire découvrir aux voyageurs internationaux des artisans locaux et corners éphémères parisiens.',
    points: ['Quote-part réservée (20%)', 'Visibilité garantie', 'Valorisation du territoire'],
  },
]

const steps = [
  { num: '1', title: 'Le voyageur exprime un besoin', desc: 'Le LLM embarqué capte une intention : faim, ennui, souvenir à acheter, correspondance longue.' },
  { num: '2', title: 'L\'algorithme consulte les enchères', desc: 'Le moteur croise l\'intention, la zone, la langue et les campagnes actives pour sélectionner la meilleure recommendation.' },
  { num: '3', title: 'Recommandation vocale contextuelle', desc: 'Le robot formule une suggestion naturelle et non intrusive, intégrée à la conversation en cours.' },
]

const faqs = [
  { q: 'Combien coûte une campagne geroAds ?', a: 'Vous définissez votre budget total et votre enchère par impression. Le système ne dépense pas plus que votre budget quotidien max. Les commerces bénéficient également d\'une indexation organique gratuite.' },
  { q: 'Comment sont ciblés les voyageurs ?', a: 'Le ciblage est exclusivement contextuel : intention vocale détectée par le LLM, langue parlée, heure de la journée, et zone d\'embarquement. Aucune donnée personnelle ou biométrique n\'est conservée.' },
  { q: 'Puis-je cibler une zone spécifique du terminal ?', a: 'Oui. Vous pouvez choisir parmi les zones : T2F Nord, Sud, Central, Satellite, ou l\'ensemble du terminal. Idéal pour les commerces de proximité.' },
  { q: 'Qu\'est-ce que le mode Flash anti-gaspillage ?', a: 'Une stratégie d\'enchère accélérée pour écouler les stocks périssables en heures creuses (avant 10h, après 14h). Vos produits sont mis en avant à coût réduit.' },
  { q: 'Le système est-il déjà déployé ailleurs qu\'au T2F ?', a: 'Actuellement en phase pilote au Terminal 2F de Roissy-CDG. L\'architecture est conçue pour être déployée dans d\'autres terminaux, gares et lieux de transit.' },
]

function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="faq-item">
      <button className={`faq-q ${open ? 'open' : ''}`} onClick={() => setOpen(!open)}>
        {q}
        <span className="material-symbols-outlined">expand_more</span>
      </button>
      <div className={`faq-a ${open ? 'open' : ''}`}>{a}</div>
    </div>
  )
}

export default function AdSolutionsPage() {
  return (
    <>
      <section className="page-hero">
        <h1>Des solutions publicitaires pour <span>chaque commerce</span></h1>
        <p>
          Que vous soyez une grande enseigne ou un artisan local, geroAds vous offre une visibilité
          auprès des voyageurs du Terminal 2F, au moment où ils en ont besoin.
        </p>
        <Link href="/login"><button className="btn btn-primary">Lancer une campagne</button></Link>
      </section>

      <div className="container">
        <div className="solution-cards">
          {solutions.map((s, i) => (
            <div key={i} className="solution-card">
              <div className="card-icon"><span className="material-symbols-outlined">{s.icon}</span></div>
              <span className={`tag ${s.tagClass}`}>{s.tag}</span>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
              <ul>
                {s.points.map((p, j) => (
                  <li key={j}><span className="material-symbols-outlined">check_circle</span>{p}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="location-banner">
          <span className="material-symbols-outlined">flight_takeoff</span>
          <p><strong>Terminal 2F — Roissy-CDG</strong> &middot; Actuellement en phase pilote. Architecture conçue pour un déploiement multi-sites (gares, centres commerciaux, aéroports).</p>
        </div>

        <section className="steps-section">
          <h2>Comment ça marche</h2>
          <div className="steps-grid">
            {steps.map((s, i) => (
              <div key={i} className="step-card">
                <div className="step-num">{s.num}</div>
                <h4>{s.title}</h4>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="faq-section">
          <h2>Questions fréquentes</h2>
          {faqs.map((f, i) => <FaqItem key={i} q={f.q} a={f.a} />)}
        </section>
      </div>

      <footer className="footer">
        GeroAds — Module de monétisation contextuelle pour Unitree G1 &middot; Terminal 2F CDG &middot; Projet GERO
      </footer>
    </>
  )
}
