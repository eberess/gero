'use client'
import Link from 'next/link'
import { useAuth } from '@/lib/auth'

const features = [
  {
    icon: 'campaign',
    title: 'Native Advertising vocal',
    desc: 'Des recommandations fluides intégrées aux conversations du robot, sans écran. Une immersion totale pour le voyageur.',
  },
  {
    icon: 'balance',
    title: 'Algorithme équitable',
    desc: 'Indexation organique gratuite pour tous, enchères premium pour les grandes enseignes, et 20% dédié aux artisans locaux.',
  },
  {
    icon: 'security',
    title: 'RGPD by design',
    desc: "Profilage contextuel uniquement : langue, heure, zone d'embarquement. Aucune donnée biométrique. Traitement on-device.",
  },
  {
    icon: 'bar_chart',
    title: 'Pilotage temps réel',
    desc: 'Dashboard commerçant et console admin ADP avec statistiques détaillées, ROI, et modération des campagnes.',
  },
  {
    icon: 'timer',
    title: 'Mode Anti-Gaspillage',
    desc: 'Enchères Flash pour écouler les stocks périssables en heures creuses. Une opportunité pour les commerces de proximité.',
  },
  {
    icon: 'memory',
    title: 'Optimisé LLM embarqué',
    desc: 'API légère pensée pour les agents LLM sur Jetson Orin NX (100 TOPS). Réponses en moins de 200ms.',
  },
]

const stats = [
  { num: '1M+', label: 'Voyageurs T2F / mois' },
  { num: '120+', label: 'Commerces référencés' },
  { num: '<200ms', label: 'Temps de réponse API' },
]

export default function LandingPage() {
  const { user } = useAuth()

  return (
    <>
      <section className="hero">
        <div className="hero-badge">
          <span className="material-symbols-outlined" style={{fontSize:'16px'}}>new_releases</span>
          Nouveau — Module geroAds v1.0
        </div>
        <h1>
          La publicité contextuelle<br />pour le robot <span>G1</span>
        </h1>
        <p>
          GeroAds transforme le robot Unitree G1 en hub de services proactif au Terminal 2F de Roissy-CDG.
          Recommandations intelligentes, enchères contextuelles, et valorisation de l&apos;artisanat local.
        </p>
        <div className="cta-group">
          {user ? (
            <Link href="/dashboard"><button className="btn btn-primary">Accéder au tableau de bord</button></Link>
          ) : (
            <>
              <Link href="/ad-solutions"><button className="btn btn-primary">Découvrir les solutions</button></Link>
              <Link href="/login"><button className="btn btn-outline">Connexion</button></Link>
            </>
          )}
        </div>

        <div className="hero-stats">
          {stats.map((s, i) => (
            <div key={i} className="hero-stat">
              <div className="num">{s.num}</div>
              <div className="label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="container">
        <section className="features-section">
          <h2>Une plateforme complète</h2>
          <p className="section-sub">Pensée pour les commerçants, les voyageurs, et les équipes ADP</p>
          <div className="features-grid">
            {features.map((f, i) => (
              <Link key={i} href={i < 2 ? '/ad-solutions' : i < 4 ? '/analytics' : '/ad-solutions'} style={{textDecoration:'none'}}>
                <div className="feature-card">
                  <div className="icon">
                    <span className="material-symbols-outlined">{f.icon}</span>
                  </div>
                  <h3>{f.title}</h3>
                  <p>{f.desc}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="cta-section">
          <h2>Prêt à lancer vos campagnes ?</h2>
          <p>Rejoignez les commerçants du Terminal 2F et boostez votre visibilité auprès des voyageurs.</p>
          <div style={{display:'flex', gap:'0.75rem', justifyContent:'center', flexWrap:'wrap'}}>
            <Link href="/ad-solutions"><button className="btn btn-outline" style={{background:'transparent',color:'white',borderColor:'rgba(255,255,255,0.4)'}}>Découvrir les solutions</button></Link>
            {user ? (
              <Link href="/campaigns/create"><button className="btn">Créer une campagne</button></Link>
            ) : (
              <Link href="/login"><button className="btn">Connexion</button></Link>
            )}
          </div>
        </section>
      </div>

      <footer className="footer">
        GeroAds — Module de monétisation contextuelle pour Unitree G1 &middot; Terminal 2F CDG &middot; Projet GERO
      </footer>
    </>
  )
}
