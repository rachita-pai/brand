/**
 * PAI Logo Component
 *
 * Usage:
 * import Logo from '@/components/Logo';
 * <Logo />
 *
 * To use a custom logo image:
 * 1. Add pai_logo_full.png to /public directory
 * 2. Uncomment the Image component below
 * 3. Comment out the text version
 */

// import Image from 'next/image';

export default function Logo() {
  // Text version (current)
  return (
    <div className="logo">
      <span className="heading" style={{ margin: 0 }}>
        PAI
      </span>
    </div>
  );

  // Image version (uncomment when you add logo file)
  /*
  return (
    <div className="logo">
      <Image
        src="/pai_logo_full.png"
        alt="PAI Logo"
        className="logo-image"
        width={80}
        height={30}
        priority
      />
    </div>
  );
  */
}
