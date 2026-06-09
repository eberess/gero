'use client'
import { useState } from 'react'
import Link from 'next/link'

const metrics = [
  { icon: 'visibility', title: 'Impressions', desc: 'Nombre de fois où votre enseigne est recommandée vocalement par le robot. Chaque interaction est comptabilisée.' },
  { icon: 'ads_click', title: 'Taux d\'engagement', desc: 'Pourcentage de voyageurs qui interagissent avec la recommandation (demande d\'itinéraire, question supplémentaire).' },
  { icon: 'trending_up', title: 'ROI publicitaire', desc: 'Retour sur investissement calculé automatiquement en fonction de votre budget et des interactions générées.' },
  { icon: 'groups', title: 'Audience atteinte', desc: 'Nombre de voyageurs uniques exposés à vos recommandations, ventilé par langue, heure et zone.' },
]

const steps = [
  { num: '1', title: 'Collecte contextuelle', desc: 'Chaque interaction est enregistrée de manière anonyme : intention, langue, zone, horaire. Aucune donnée personnelle.' },
  { num: '2', title: 'Tableau de bord temps réel', desc: 'Visualisez vos campagnes, impressions et budget consommé en direct depuis le Gero Business Portal.' },
  { num: '3', title: 'Optimisation continue', desc: 'Ajustez vos enchères, mots-clés et zones en fonction des performances constatées pour maximiser votre ROI.' },
]

const faqs = [
  { q: 'Quelles données sont collectées ?', a: 'Uniquement des données contextuelles anonymes : intention vocale détectée, langue, heure, zone d\'embarquement. Aucune donnée biométrique, aucun identifiant personnel. Conforme RGPD.' },
  { q: 'Puis-je exporter mes données ?', a: 'Oui. L\'API geroAds expose les données de campagnes et d\'impressions au format JSON, utilisable dans vos outils BI (Power BI, Tableau, Google Looker).' },
  { q: 'À quelle fréquence les statistiques sont-elles mises à jour ?', a: 'En temps réel. Les impressions sont comptabilisées instantanément et le dashboard se met à jour à chaque recommandation.' },
  { q: 'Puis-je comparer mes performances sur différentes périodes ?', a: 'Oui. Le dashboard propose des vues par jour, semaine, mois et personnalisables. Vous pouvez également exporter l\'historique complet.' },
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

export default function AnalyticsPage() {
  return (
    <>
      <section className="page-hero">
        <h1>Pilotez vos campagnes <span>en temps réel</span></h1>
        <p>
          Visualisez l&apos;impact de vos campagnes publicitaires vocales : impressions, engagement,
          budget consommé et ROI. Des données claires pour des décisions éclairées.
        </p>
        <Link href="/login"><button className="btn btn-primary">Accéder au dashboard</button></Link>
      </section>

      <div className="container">
        <div className="solution-cards">
          {metrics.map((m, i) => (
            <div key={i} className="solution-card">
              <div className="card-icon"><span className="material-symbols-outlined">{m.icon}</span></div>
              <h3>{m.title}</h3>
              <p>{m.desc}</p>
            </div>
          ))}
        </div>

        <div className="use-case">
          <div className="use-case-visual">
            <span className="material-symbols-outlined">monitoring</span>
          </div>
          <div className="use-case-text">
            <h3>Exemple concret</h3>
            <p>
              Une boulangerie Paul au T2F Central a investi <span className="highlight">200€</span> sur une campagne
              contextuelle ciblant le mot-clé &quot;petit-déjeuner&quot; entre 6h et 10h.
              Résultat : <span className="highlight">1 240 impressions</span> en 2 semaines,
              soit un coût par impression de <span className="highlight">0,16€</span>.
            </p>
          </div>
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
